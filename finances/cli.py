"""Command-line interface for finance tracking."""

import click
from rich.console import Console
from rich.table import Table

from finances.database import init_db, SessionLocal

console = Console()


@click.group()
def cli():
    """Personal finance tracker - aggregate and analyze spending."""
    pass


@cli.command()
def init():
    """Initialize the database."""
    init_db()
    console.print("[green]Database initialized successfully.[/green]")


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
    """List spending categories and budgets."""
    from finances.models import Category

    db = SessionLocal()
    try:
        cats = db.query(Category).filter(Category.parent_id.is_(None)).all()
        if not cats:
            console.print("No categories defined. Use 'add-category' to create one.")
            return

        table = Table(title="Categories")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Monthly Budget", justify="right")

        for cat in cats:
            budget = f"${cat.budget_monthly:,.2f}" if cat.budget_monthly else "-"
            table.add_row(str(cat.id), cat.name, budget)

        console.print(table)
    finally:
        db.close()


@cli.command()
@click.argument("name")
@click.option("--budget", "-b", type=float, help="Monthly budget amount")
def add_category(name: str, budget: float | None):
    """Add a spending category."""
    from finances.models import Category

    db = SessionLocal()
    try:
        cat = Category(name=name, budget_monthly=budget)
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


if __name__ == "__main__":
    cli()
