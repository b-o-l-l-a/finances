"""Transaction sync service - imports transactions from Plaid into the database."""

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from finances.models import Account, Transaction, TransactionSource
from finances.plaid_service import get_transactions, get_accounts


def sync_account_transactions(
    db: Session,
    account: Account,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """
    Sync transactions from Plaid for a specific account.

    Args:
        db: Database session
        account: Account model instance with plaid_access_token
        start_date: Start of date range (default: 30 days ago)
        end_date: End of date range (default: today)

    Returns:
        Dict with sync statistics: {added, skipped, total}
    """
    if not account.plaid_access_token:
        raise ValueError(f"Account {account.name} has no Plaid access token")

    # Fetch transactions from Plaid
    plaid_transactions = get_transactions(
        account.plaid_access_token,
        start_date=start_date,
        end_date=end_date,
    )

    stats = {"added": 0, "skipped": 0, "total": len(plaid_transactions)}

    for plaid_txn in plaid_transactions:
        # Check for duplicate by plaid_transaction_id
        existing = (
            db.query(Transaction)
            .filter(Transaction.plaid_transaction_id == plaid_txn.transaction_id)
            .first()
        )

        if existing:
            stats["skipped"] += 1
            continue

        # Create new transaction
        # Plaid amounts: positive = money out (expense), negative = money in (income)
        # We store: negative = expense, positive = income
        amount = Decimal(str(plaid_txn.amount)) * -1

        txn = Transaction(
            date=plaid_txn.date,
            amount=amount,
            merchant=plaid_txn.merchant_name or plaid_txn.name,
            description=plaid_txn.name,
            source=TransactionSource.PLAID,
            plaid_transaction_id=plaid_txn.transaction_id,
            account_id=account.id,
            # Category mapping could be added here based on plaid_txn.category
        )

        db.add(txn)
        stats["added"] += 1

    # Update last synced timestamp
    account.last_synced = datetime.now(timezone.utc)

    db.commit()
    return stats


def create_account_from_plaid(
    db: Session,
    access_token: str,
    institution_name: str,
    plaid_accounts: list[dict],
) -> list[Account]:
    """
    Create Account records from Plaid account data.

    Args:
        db: Database session
        access_token: Plaid access token to store
        institution_name: Name of the institution
        plaid_accounts: List of account dicts from Plaid metadata

    Returns:
        List of created Account instances
    """
    from finances.models import Institution, AccountType

    # Map institution name to enum
    institution_map = {
        "usaa": Institution.USAA,
        "us bank": Institution.US_BANK,
        "u.s. bank": Institution.US_BANK,
    }

    institution = None
    for key, inst_enum in institution_map.items():
        if key in institution_name.lower():
            institution = inst_enum
            break

    if institution is None:
        # Default - you may want to handle this differently
        raise ValueError(
            f"Unknown institution: {institution_name}. "
            f"Add it to the Institution enum in models.py"
        )

    # Map Plaid account types to our enum
    type_map = {
        "depository": {
            "checking": AccountType.CHECKING,
            "savings": AccountType.SAVINGS,
        },
        "credit": {
            "credit card": AccountType.CREDIT,
        },
    }

    created_accounts = []

    for plaid_acct in plaid_accounts:
        # Check if account already exists
        existing = (
            db.query(Account)
            .filter(Account.plaid_account_id == plaid_acct.get("id"))
            .first()
        )

        if existing:
            # Update access token in case it changed
            existing.plaid_access_token = access_token
            created_accounts.append(existing)
            continue

        # Determine account type
        acct_type = plaid_acct.get("type", "depository")
        acct_subtype = plaid_acct.get("subtype", "checking")

        account_type = type_map.get(acct_type, {}).get(
            acct_subtype, AccountType.CHECKING
        )

        account = Account(
            name=plaid_acct.get("name", f"{institution_name} Account"),
            institution=institution,
            account_type=account_type,
            plaid_account_id=plaid_acct.get("id"),
            plaid_access_token=access_token,
        )

        db.add(account)
        created_accounts.append(account)

    db.commit()
    return created_accounts
