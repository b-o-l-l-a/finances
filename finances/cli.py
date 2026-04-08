"""Command-line interface for finance tracking."""

import click
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table

from finances.database import init_db, SessionLocal

console = Console()


# HTML template for Teller Connect
TELLER_CONNECT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Connect Your Bank</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        button {{
            background: #0066cc;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{ background: #0052a3; }}
        .success {{ color: #28a745; }}
        .error {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Connect Your Bank Account</h1>
        <p>Click the button below to securely connect your bank via Teller.</p>
        <button id="connect-btn">Connect Bank</button>
        <p id="status"></p>
    </div>
    <script src="https://cdn.teller.io/connect/connect.js"></script>
    <script>
        const tellerConnect = TellerConnect.setup({{
            applicationId: "{application_id}",
            environment: "{environment}",
            onSuccess: function(enrollment) {{
                document.getElementById('status').innerHTML = '<span class="success">Connected! You can close this window.</span>';
                fetch('/callback', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(enrollment)
                }});
            }},
            onExit: function() {{
                document.getElementById('status').innerHTML = '<span class="error">Connection cancelled.</span>';
            }}
        }});
        document.getElementById('connect-btn').addEventListener('click', function() {{
            tellerConnect.open();
        }});
    </script>
</body>
</html>
"""


@click.group()
def cli():
    """Personal finance tracker - aggregate and analyze spending."""
    pass


@cli.command()
@click.option("--seed", is_flag=True, help="Also seed categories and rules")
def init(seed: bool):
    """Initialize the database."""
    init_db()
    console.print("[green]Database initialized.[/green]")

    if seed:
        from finances.seed import seed_all
        seed_all()


@cli.command()
def accounts():
    """List connected accounts."""
    from finances.models import Account

    db = SessionLocal()
    try:
        accts = db.query(Account).all()
        if not accts:
            console.print("No accounts connected. Use 'link' to connect a bank.")
            return

        table = Table(title="Connected Accounts")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Institution")
        table.add_column("Type")
        table.add_column("Last Synced")

        for acct in accts:
            table.add_row(
                str(acct.id),
                acct.name,
                acct.institution.display_name,
                acct.account_type.display_name,
                str(acct.last_synced) if acct.last_synced else "Never",
            )

        console.print(table)
    finally:
        db.close()


@cli.command()
def categories():
    """List spending categories and budgets as a tree."""
    from finances.models import Category

    db = SessionLocal()
    try:
        roots = db.query(Category).filter(Category.parent_id.is_(None)).all()
        if not roots:
            console.print("No categories defined. Use 'add-category' to create one.")
            return

        table = Table(title="Categories")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Monthly Budget", justify="right")

        def add_category_rows(parent_id: int | None, indent: int = 0) -> None:
            cats = db.query(Category).filter(
                Category.parent_id == parent_id
            ).order_by(Category.name).all()

            for cat in cats:
                prefix = "  " * indent + ("└── " if indent > 0 else "")
                budget = f"${cat.budget_monthly:,.2f}" if cat.budget_monthly else "-"
                table.add_row(str(cat.id), f"{prefix}{cat.name}", budget)
                add_category_rows(cat.id, indent + 1)

        add_category_rows(None)
        console.print(table)
    finally:
        db.close()


@cli.command()
@click.argument("name")
@click.option("--budget", "-b", type=float, help="Monthly budget amount")
@click.option("--parent", "-p", help="Parent category name")
def add_category(name: str, budget: float | None, parent: str | None):
    """Add a spending category."""
    from finances.models import Category

    db = SessionLocal()
    try:
        parent_id = None
        if parent:
            parent_cat = db.query(Category).filter(Category.name.ilike(parent)).first()
            if not parent_cat:
                console.print(f"[red]Parent category '{parent}' not found.[/red]")
                return
            parent_id = parent_cat.id

        cat = Category(name=name, budget_monthly=budget, parent_id=parent_id)
        db.add(cat)
        db.commit()
        console.print(f"[green]Category '{name}' created.[/green]")
    finally:
        db.close()


@cli.command()
def spending():
    """Show spending by category for current month."""
    from datetime import date
    from sqlalchemy import func, extract
    from finances.models import Transaction, Category

    db = SessionLocal()
    try:
        today = date.today()

        results = (
            db.query(
                Category.name,
                Category.budget_monthly,
                func.sum(Transaction.amount).label("spent"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                extract("year", Transaction.date) == today.year,
                extract("month", Transaction.date) == today.month,
                Transaction.amount < 0,
            )
            .group_by(Category.id)
            .all()
        )

        if not results:
            console.print("No transactions this month.")
            return

        table = Table(title=f"Spending - {today.strftime('%B %Y')}")
        table.add_column("Category")
        table.add_column("Spent", justify="right")
        table.add_column("Budget", justify="right")
        table.add_column("%", justify="right")

        for name, budget, spent in results:
            spent_abs = abs(spent)
            spent_str = f"${spent_abs:,.2f}"
            budget_str = f"${budget:,.2f}" if budget else "-"

            if budget:
                pct = (spent_abs / float(budget)) * 100
                pct_str = f"{pct:.0f}%"
                if pct >= 90:
                    pct_str = f"[red]{pct_str} ⚠️[/red]"
                elif pct >= 75:
                    pct_str = f"[yellow]{pct_str}[/yellow]"
            else:
                pct_str = "-"

            table.add_row(name, spent_str, budget_str, pct_str)

        console.print(table)
    finally:
        db.close()


@cli.command()
@click.option("--limit", "-n", default=20, help="Number of transactions to show")
def transactions(limit: int):
    """List recent transactions."""
    from finances.models import Transaction

    db = SessionLocal()
    try:
        txns = (
            db.query(Transaction)
            .order_by(Transaction.date.desc())
            .limit(limit)
            .all()
        )

        if not txns:
            console.print("No transactions yet.")
            return

        table = Table(title="Recent Transactions")
        table.add_column("Date")
        table.add_column("Merchant")
        table.add_column("Amount", justify="right")
        table.add_column("Category")
        table.add_column("Source", style="dim")

        for txn in txns:
            amount_str = f"${abs(txn.amount):,.2f}"
            if txn.amount < 0:
                amount_str = f"[red]-{amount_str}[/red]"
            else:
                amount_str = f"[green]+{amount_str}[/green]"

            table.add_row(
                str(txn.date),
                txn.merchant[:30],
                amount_str,
                txn.category.name if txn.category else "-",
                txn.source.value,
            )

        console.print(table)
    finally:
        db.close()


@cli.command()
def link():
    """Connect a bank account via Teller."""
    import json
    import os
    import webbrowser
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse

    from finances.models import Account, Institution, AccountType
    from finances.teller import TellerClient, map_teller_account_type

    app_id = os.getenv("TELLER_APPLICATION_ID")
    env = os.getenv("TELLER_ENV", "sandbox")

    if not app_id:
        console.print("[red]Error: TELLER_APPLICATION_ID not set in .env[/red]")
        return

    enrollment_data = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress HTTP server logs

        def do_GET(self):
            if urlparse(self.path).path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html = TELLER_CONNECT_HTML.format(
                    application_id=app_id,
                    environment=env
                )
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if urlparse(self.path).path == "/callback":
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                enrollment_data.update(json.loads(post_data))

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')

    server = HTTPServer(("127.0.0.1", 8080), CallbackHandler)
    console.print("Starting Teller Connect...")
    console.print("Opening browser at [cyan]http://127.0.0.1:8080[/cyan]")
    console.print("Press Ctrl+C after connecting your bank.\n")

    webbrowser.open("http://127.0.0.1:8080")

    try:
        while not enrollment_data:
            server.handle_request()
        # Handle a few more requests to complete the flow
        server.timeout = 1
        for _ in range(3):
            try:
                server.handle_request()
            except Exception:
                break
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    if not enrollment_data:
        console.print("[yellow]No enrollment data received.[/yellow]")
        return

    access_token = enrollment_data.get("accessToken")
    institution_info = enrollment_data.get("enrollment", {}).get("institution", {})
    institution_name = institution_info.get("name", "Unknown")

    console.print(f"\n[green]Successfully connected to {institution_name}![/green]")

    # Fetch accounts using the access token
    client = TellerClient(access_token)

    try:
        accounts = client.list_accounts()
    except Exception as e:
        console.print(f"[red]Error fetching accounts: {e}[/red]")
        return

    db = SessionLocal()
    try:
        for acct_data in accounts:
            # Check if account already exists
            existing = db.query(Account).filter(
                Account.external_account_id == acct_data["id"]
            ).first()

            if existing:
                console.print(f"  Account {acct_data['name']} already linked.")
                continue

            # Map account type
            acct_type_str = map_teller_account_type(
                acct_data.get("type", "depository"),
                acct_data.get("subtype", "checking")
            )

            # Try to match institution, default to USAA for now
            try:
                institution = Institution.USAA  # Default
                inst_name_lower = institution_name.lower()
                if "us bank" in inst_name_lower:
                    institution = Institution.US_BANK
                elif "usaa" in inst_name_lower:
                    institution = Institution.USAA
            except Exception:
                institution = Institution.USAA

            # Map account type
            try:
                account_type = AccountType(acct_type_str)
            except ValueError:
                account_type = AccountType.CHECKING

            account = Account(
                name=acct_data.get("name", "Unknown Account"),
                institution=institution,
                account_type=account_type,
                external_account_id=acct_data["id"],
                access_token=access_token,
            )
            db.add(account)
            console.print(f"  [green]Linked: {account.name} ({account_type.display_name})[/green]")

        db.commit()
        console.print("\n[green]Account linking complete![/green]")
    finally:
        db.close()


@cli.command()
@click.option("--account-id", "-a", type=int, help="Sync specific account by ID")
@click.option("--count", "-n", default=100, help="Number of transactions to fetch per account (default 100)")
def sync(account_id: int | None, count: int):
    """Sync transactions from connected bank accounts."""
    from finances.models import Account, Transaction, TransactionSource
    from finances.teller import TellerClient, parse_teller_date

    db = SessionLocal()
    try:
        if account_id:
            accounts = db.query(Account).filter(Account.id == account_id).all()
        else:
            accounts = db.query(Account).filter(Account.access_token.isnot(None)).all()

        if not accounts:
            console.print("No connected accounts to sync. Use 'link' to connect a bank.")
            return

        total_new = 0

        for account in accounts:
            console.print(f"Syncing [cyan]{account.name}[/cyan]...")

            client = TellerClient(account.access_token)

            try:
                transactions = client.list_transactions(account.external_account_id, count=count)
            except Exception as e:
                console.print(f"  [red]Error: {e}[/red]")
                continue

            new_count = 0
            for txn_data in transactions:
                # Skip if transaction already exists
                existing = db.query(Transaction).filter(
                    Transaction.external_transaction_id == txn_data["id"]
                ).first()

                if existing:
                    continue

                # Parse transaction amount
                # "debit" and "credit" types: Teller sends positive amounts, we apply sign
                # All other known types: amount is already correctly signed by Teller/bank
                amount = float(txn_data.get("amount", 0))
                txn_type = txn_data.get("type")
                if txn_type == "debit":
                    amount = -abs(amount)
                elif txn_type == "credit":
                    amount = abs(amount)
                elif txn_type in (
                    "card_payment", "check", "deposit", "fee",
                    "interest", "payment", "transaction", "transfer", "withdrawal",
                ):
                    pass  # amount is already correctly signed
                else:
                    raise ValueError(f"Unknown transaction type: {txn_type}")

                details = txn_data.get("details", {})
                counterparty = details.get("counterparty") or {}
                merchant = counterparty.get("name") or txn_data.get("description", "Unknown")
                
                console.print(f"  [dim]type={txn_type} amount={amount} merchant={merchant}[/dim]")

                txn = Transaction(
                    date=parse_teller_date(txn_data["date"]),
                    amount=amount,
                    merchant=merchant,
                    description=txn_data.get("description", ""),
                    source=TransactionSource.TELLER,
                    external_transaction_id=txn_data["id"],
                    account_id=account.id,
                )
                db.add(txn)
                new_count += 1

            account.last_synced = datetime.now(timezone.utc)
            total_new += new_count
            console.print(f"  [green]{new_count} new transactions[/green]")

        db.commit()
        console.print(f"\n[green]Sync complete! {total_new} new transactions added.[/green]")
    finally:
        db.close()


@cli.command()
@click.argument("transaction_id", type=int)
@click.argument("category_name")
def categorize(transaction_id: int, category_name: str):
    """Manually assign a category to a transaction."""
    from finances.models import Transaction, Category

    db = SessionLocal()
    try:
        txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not txn:
            console.print(f"[red]Transaction {transaction_id} not found.[/red]")
            return

        category = db.query(Category).filter(Category.name.ilike(category_name)).first()
        if not category:
            console.print(f"[red]Category '{category_name}' not found.[/red]")
            return

        txn.category_id = category.id
        db.commit()
        console.print(f"[green]Transaction {transaction_id} categorized as '{category.name}'.[/green]")
    finally:
        db.close()


@cli.command()
@click.argument("pattern")
@click.argument("category_name")
@click.option("--min", "min_amount", type=float, help="Minimum absolute amount for rule to match")
@click.option("--max", "max_amount", type=float, help="Maximum absolute amount for rule to match")
def add_rule(pattern: str, category_name: str, min_amount: float | None, max_amount: float | None):
    """Add a rule to auto-categorize transactions by merchant pattern.

    Optionally specify --min and --max for amount-based conditions.
    Example: add-rule "7-eleven" "Food" --max 20
    """
    from finances.models import Category, CategoryRule

    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.name.ilike(category_name)).first()
        if not category:
            console.print(f"[red]Category '{category_name}' not found.[/red]")
            return

        # Check for duplicate rule with same pattern AND amount conditions
        existing = db.query(CategoryRule).filter(
            CategoryRule.pattern.ilike(pattern),
            CategoryRule.min_abs_amount == min_amount,
            CategoryRule.max_abs_amount == max_amount
        ).first()
        if existing:
            console.print(f"[yellow]Rule for '{pattern}' with same conditions already exists (→ {existing.category.name}).[/yellow]")
            return

        rule = CategoryRule(
            pattern=pattern.lower(),
            category_id=category.id,
            min_abs_amount=min_amount,
            max_abs_amount=max_amount
        )
        db.add(rule)
        db.commit()

        # Build description
        conditions = []
        if min_amount:
            conditions.append(f">=${min_amount}")
        if max_amount:
            conditions.append(f"<${max_amount}")
        condition_str = f" ({', '.join(conditions)})" if conditions else ""

        console.print(f"[green]Rule added: '{pattern}'{condition_str} → {category.name}[/green]")
    finally:
        db.close()


@cli.command()
def rules():
    """List categorization rules."""
    from finances.models import CategoryRule

    db = SessionLocal()
    try:
        all_rules = db.query(CategoryRule).order_by(CategoryRule.pattern).all()
        if not all_rules:
            console.print("No rules defined. Use 'add-rule' to create one.")
            return

        table = Table(title="Categorization Rules")
        table.add_column("ID", style="dim")
        table.add_column("Pattern")
        table.add_column("Amount Condition")
        table.add_column("Category")

        for rule in all_rules:
            conditions = []
            if rule.min_abs_amount:
                conditions.append(f">=${rule.min_abs_amount}")
            if rule.max_abs_amount:
                conditions.append(f"<${rule.max_abs_amount}")
            condition_str = ", ".join(conditions) if conditions else "-"
            table.add_row(str(rule.id), rule.pattern, condition_str, rule.category.name)

        console.print(table)
    finally:
        db.close()


@cli.command()
def manual_categorize():
    """Interactively categorize uncategorized transactions."""
    from finances.models import Transaction, Category

    db = SessionLocal()
    try:
        while True:
            # Get uncategorized transactions
            uncategorized = (
                db.query(Transaction)
                .filter(Transaction.category_id.is_(None))
                .order_by(Transaction.date.desc())
                .all()
            )

            if not uncategorized:
                console.print("[green]No uncategorized transactions remaining![/green]")
                break

            console.print(f"\n[bold]Uncategorized transactions ({len(uncategorized)}):[/bold]\n")

            # Show transactions with index
            table = Table()
            table.add_column("#", style="dim")
            table.add_column("Date")
            table.add_column("Amount", justify="right")
            table.add_column("Merchant")
            table.add_column("Account", style="dim")

            for i, txn in enumerate(uncategorized[:20], 1):  # Show first 20
                amount_str = f"${abs(txn.amount):,.2f}"
                if txn.amount < 0:
                    amount_str = f"[red]-{amount_str}[/red]"
                else:
                    amount_str = f"[green]+{amount_str}[/green]"
                account_name = txn.account.name if txn.account else "-"
                table.add_row(str(i), str(txn.date), amount_str, txn.merchant[:50], account_name)

            console.print(table)

            if len(uncategorized) > 20:
                console.print(f"[dim]...and {len(uncategorized) - 20} more[/dim]")

            # Prompt for transaction selection
            console.print("\n[cyan]Enter transaction # to categorize (or 'q' to quit, 's' to skip):[/cyan]")
            choice = input("> ").strip().lower()

            if choice == 'q':
                break
            if choice == 's':
                continue

            try:
                txn_idx = int(choice) - 1
                if txn_idx < 0 or txn_idx >= len(uncategorized[:20]):
                    console.print("[red]Invalid selection.[/red]")
                    continue
            except ValueError:
                console.print("[red]Please enter a number, 'q', or 's'.[/red]")
                continue

            selected_txn = uncategorized[txn_idx]
            console.print(f"\nSelected: [bold]{selected_txn.merchant}[/bold] ({selected_txn.date}, ${abs(selected_txn.amount):,.2f})")

            # Show categories
            def get_categories_flat(parent_id=None, prefix=""):
                """Get categories as flat list with indentation."""
                cats = db.query(Category).filter(
                    Category.parent_id == parent_id
                ).order_by(Category.name).all()
                result = []
                for cat in cats:
                    result.append((cat, prefix + cat.name))
                    result.extend(get_categories_flat(cat.id, prefix + "  "))
                return result

            categories_flat = get_categories_flat()

            console.print("\n[bold]Categories:[/bold]")
            cat_table = Table(show_header=False, box=None)
            cat_table.add_column("#", style="dim", width=4)
            cat_table.add_column("Name")

            for i, (cat, display_name) in enumerate(categories_flat, 1):
                cat_table.add_row(str(i), display_name)

            console.print(cat_table)

            # Prompt for category selection
            console.print("\n[cyan]Enter category # or name (or 's' to skip):[/cyan]")
            cat_choice = input("> ").strip()

            if cat_choice.lower() == 's':
                continue

            selected_cat = None

            # Try as number first
            try:
                cat_idx = int(cat_choice) - 1
                if 0 <= cat_idx < len(categories_flat):
                    selected_cat = categories_flat[cat_idx][0]
            except ValueError:
                # Try as name match
                for cat, _ in categories_flat:
                    if cat.name.lower() == cat_choice.lower():
                        selected_cat = cat
                        break

            if not selected_cat:
                console.print("[red]Invalid category selection.[/red]")
                continue

            # Confirm before applying
            amount_str = f"-${abs(selected_txn.amount):,.2f}" if selected_txn.amount < 0 else f"+${abs(selected_txn.amount):,.2f}"
            console.print(f"\n[yellow]Categorize '[bold]{selected_txn.merchant[:40]}[/bold]' ({selected_txn.date}, {amount_str}) as '[bold]{selected_cat.name}[/bold]'?[/yellow]")
            console.print("[cyan]Enter 'y' to confirm, any other key to cancel:[/cyan]")
            confirm = input("> ").strip().lower()

            if confirm != 'y':
                console.print("[dim]Cancelled.[/dim]")
                continue

            # Apply categorization
            selected_txn.category_id = selected_cat.id
            db.commit()
            console.print(f"[green]Categorized as '{selected_cat.name}'[/green]")

            # Offer to create a rule
            console.print(f"\n[cyan]Add a rule to auto-categorize future transactions as '{selected_cat.name}'? (y/n):[/cyan]")
            if input("> ").strip().lower() == 'y':
                console.print(f"[cyan]Pattern (enter to use '{selected_txn.merchant.lower()}'):[/cyan]")
                pattern = input("> ").strip().lower() or selected_txn.merchant.lower()
                if pattern:
                    from finances.models import CategoryRule
                    rule = CategoryRule(pattern=pattern, category_id=selected_cat.id)
                    db.add(rule)
                    db.commit()
                    console.print(f"[green]Rule added: '{pattern}' → {selected_cat.name}[/green]")

    finally:
        db.close()


@cli.command()
@click.option("--dry-run", is_flag=True, help="Show what would be categorized without saving")
def auto_categorize(dry_run: bool):
    """Apply categorization rules to uncategorized transactions."""
    from finances.models import Transaction, CategoryRule

    db = SessionLocal()
    try:
        # Sort rules: more specific rules (with amount conditions) first
        all_rules = db.query(CategoryRule).all()
        rules = sorted(all_rules, key=lambda r: (
            r.min_abs_amount is None and r.max_abs_amount is None,  # Rules with conditions first
            r.pattern
        ))

        if not rules:
            console.print("No rules defined. Use 'add-rule' to create rules first.")
            return

        uncategorized = db.query(Transaction).filter(Transaction.category_id.is_(None)).all()
        if not uncategorized:
            console.print("No uncategorized transactions.")
            return

        categorized_count = 0
        for txn in uncategorized:
            merchant_lower = txn.merchant.lower()
            abs_amount = abs(float(txn.amount))

            for rule in rules:
                if rule.pattern not in merchant_lower:
                    continue

                # Check amount conditions (min is inclusive >=, max is exclusive <)
                if rule.min_abs_amount and abs_amount < float(rule.min_abs_amount):
                    continue
                if rule.max_abs_amount and abs_amount >= float(rule.max_abs_amount):
                    continue

                # Rule matches
                if dry_run:
                    console.print(f"  {txn.merchant[:40]} (${abs_amount:.2f}) → {rule.category.name}")
                else:
                    txn.category_id = rule.category_id
                categorized_count += 1
                break

        if not dry_run:
            db.commit()
            console.print(f"[green]Categorized {categorized_count} transactions.[/green]")
        else:
            console.print(f"\n[cyan]Dry run: would categorize {categorized_count} transactions.[/cyan]")

        remaining = len(uncategorized) - categorized_count
        if remaining > 0:
            console.print(f"[yellow]{remaining} transactions still uncategorized.[/yellow]")
    finally:
        db.close()


if __name__ == "__main__":
    cli()
