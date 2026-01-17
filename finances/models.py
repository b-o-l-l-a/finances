"""Database models for finance tracking."""

from datetime import datetime, date, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String, Numeric, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from finances.database import Base


class TransactionSource(str, Enum):
    """Where the transaction data came from."""
    PLAID = "plaid"
    AMAZON_CSV = "amazon_csv"
    VENMO_CSV = "venmo_csv"
    MANUAL = "manual"


class Institution(Enum):
    """Supported financial institutions."""
    USAA = ("usaa", "USAA")
    US_BANK = ("us_bank", "US Bank")
    AMAZON = ("amazon", "Amazon")
    VENMO = ("venmo", "Venmo")

    def __init__(self, code: str, display_name: str):
        self.code = code
        self.display_name = display_name

    def __str__(self) -> str:
        return self.code


class AccountType(Enum):
    """Types of financial accounts."""
    CHECKING = ("checking", "Checking")
    SAVINGS = ("savings", "Savings")
    CREDIT = ("credit", "Credit Card")

    def __init__(self, code: str, display_name: str):
        self.code = code
        self.display_name = display_name

    def __str__(self) -> str:
        return self.code


class Account(Base):
    """A connected bank account or external service."""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))  # e.g., "USAA Checking"
    institution: Mapped[Institution] = mapped_column(
        SQLEnum(Institution, values_callable=lambda e: [i.code for i in e])
    )
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, values_callable=lambda e: [i.code for i in e])
    )
    plaid_account_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    plaid_access_token: Mapped[Optional[str]] = mapped_column(String(255))
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Category(Base):
    """Spending category with optional budget."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)  # e.g., "Groceries"
    budget_monthly: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side="Category.id", backref="subcategories"
    )
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Transaction(Base):
    """A normalized transaction from any source."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # negative = expense
    merchant: Mapped[str] = mapped_column(String(255))  # raw merchant name
    description: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[TransactionSource] = mapped_column(
        SQLEnum(TransactionSource), default=TransactionSource.MANUAL
    )

    # External IDs for deduplication
    plaid_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255))  # Amazon order ID, etc.

    # Relationships
    account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    parent_transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transactions.id")
    )

    account: Mapped[Optional["Account"]] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")
    parent_transaction: Mapped[Optional["Transaction"]] = relationship(
        "Transaction", remote_side="Transaction.id", backref="child_transactions"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.date} {self.merchant} ${self.amount}>"
