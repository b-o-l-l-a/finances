# Finances

A personal finance CLI that aggregates transactions from bank accounts and helps you categorize spending, build budgets, and track LLC business expenses for tax purposes.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). Copyleft applies — any distributed derivative work must also be released under the GPL.

## Requirements

- Python 3.11+
- A [Teller](https://teller.io) account and application ID for bank account linking

## Installation

```bash
pip install -e ".[dev]"
```

After installing, run `finances --help` to see all available commands:

```
Usage: finances [OPTIONS] COMMAND [ARGS]...

  Personal finance tracker - aggregate and analyze spending.

Commands:
  accounts           List connected accounts.
  add-category       Add a spending category.
  add-rule           Add a rule to auto-categorize transactions by merchant pattern.
  auto-categorize    Apply categorization rules to uncategorized transactions.
  business-report    Show LLC business expenses by category for tax reporting.
  categories         List spending categories and budgets as a tree.
  categorize         Manually assign a category to a transaction.
  init               Initialize the database.
  link               Connect a bank account via Teller.
  manual-categorize  Interactively categorize uncategorized transactions.
  mark-business      Interactively tag transactions as LLC business expenses.
  mark-one-time      Interactively mark transactions as one-time (excluded from budget suggestions).
  rules              List categorization rules.
  spending           Show spending by category for current month (or YTD).
  suggest-budget     Suggest monthly budgets based on average historical spending.
  sync               Sync transactions from connected bank accounts.
  transactions       List recent transactions.
```

Run `finances <command> --help` for options on any command. Key examples:

```
Usage: finances sync [OPTIONS]
  -a, --account-id INTEGER  Sync specific account by ID
  -n, --count INTEGER       Number of transactions to fetch per account (default 100)

Usage: finances suggest-budget [OPTIONS]
  -m, --months INTEGER  Number of months of history to analyze (default 3)
  --apply               Save suggested budgets to categories

Usage: finances mark-business [OPTIONS]
  -c, --category TEXT     Filter by category name
  -m, --min-amount FLOAT  Only show transactions above this amount
  -y, --year INTEGER      Filter by year (default: current year)
  -n, --limit INTEGER     Max transactions to show (default 50)

Usage: finances spending [OPTIONS]
  --ytd                     Show year-to-date instead of current month
  -a, --account-id INTEGER  Filter by account ID

Usage: finances add-rule [OPTIONS] PATTERN CATEGORY_NAME
  --min FLOAT  Minimum absolute amount for rule to match
  --max FLOAT  Maximum absolute amount for rule to match

Usage: finances add-category [OPTIONS] NAME
  -b, --budget FLOAT  Monthly budget amount
  -p, --parent TEXT   Parent category name
```

## Setup

1. Copy `.env.example` to `.env` and fill in your Teller credentials:
   ```
   TELLER_APPLICATION_ID=your_app_id
   TELLER_ENV=sandbox   # or "production"
   ```

2. Initialize the database:
   ```bash
   finances init
   ```

3. Optionally seed default categories and rules:
   ```bash
   finances init --seed
   ```

## Connecting Bank Accounts

```bash
finances link
```

Opens a browser window with Teller Connect to securely link your bank. Once linked, accounts are stored locally.

```bash
finances accounts   # list connected accounts
```

## Syncing Transactions

```bash
finances sync                    # sync all accounts (last 100 transactions)
finances sync --count 500        # fetch more history
finances sync --account-id 2     # sync a specific account
```

## Categorization

### Categories

```bash
finances categories                              # list all categories as a tree
finances add-category "Groceries"                # add a root category
finances add-category "Produce" --parent "Groceries"  # add a subcategory
finances add-category "Groceries" --budget 400   # with a monthly budget
```

### Rules

Auto-categorize transactions by merchant name pattern:

```bash
finances add-rule "whole foods" "Groceries"
finances add-rule "shell" "Gasoline" --min 20       # only if amount >= $20
finances add-rule "shell" "Groceries" --max 20      # only if amount < $20
finances rules                                       # list all rules
```

### Applying Categorization

```bash
finances auto-categorize            # apply rules to uncategorized transactions
finances auto-categorize --dry-run  # preview without saving
finances manual-categorize          # interactively categorize remaining transactions
finances categorize 42 "Groceries"  # manually assign a single transaction
```

## Viewing Transactions

```bash
finances transactions          # last 20 transactions
finances transactions -n 100   # last 100 transactions
```

## Spending Reports

```bash
finances spending              # current month, split into required vs discretionary
finances spending --ytd        # year-to-date
finances spending --account-id 2  # filter by account
```

### Transaction Amount Convention

- **Negative** = expense
- **Positive** = income

## Budgets

Generate budget suggestions based on historical spending averages:

```bash
finances suggest-budget                  # based on last 3 complete months
finances suggest-budget --months 6       # use 6 months of history
finances suggest-budget --months 6 --apply  # save suggestions to categories
```

One-time purchases (large insurance payouts, non-recurring expenses) can be excluded from budget calculations:

```bash
finances mark-one-time                          # browse all expenses
finances mark-one-time --category "Repairs"     # filter by category
finances mark-one-time --min-amount 1000        # filter by amount
```

## LLC Business Expenses

Tag transactions as business expenses for Schedule C / tax reporting:

```bash
finances mark-business --year 2025                      # tag 2025 transactions
finances mark-business --year 2025 --category "Travel"  # filter by category
```

You will be prompted for a **business purpose** on each tagged transaction — keep these notes clear for documentation purposes.

Generate a tax report:

```bash
finances business-report             # current year
finances business-report --year 2025 # specific year
```

The report shows a summary by category and a full line-item detail table.

## Development

```bash
pip install -e ".[dev]"
pytest          # run all tests
pytest tests/test_file.py::test_name  # run a single test
```

## Architecture

| File | Purpose |
|------|---------|
| `cli.py` | All CLI commands (Click-based) |
| `models.py` | SQLAlchemy 2.0 models (`Account`, `Transaction`, `Category`, `CategoryRule`) |
| `database.py` | Engine and session setup (SQLite) |
| `config.py` | Environment config via `.env` |
| `teller.py` | Teller API client |
| `seed.py` | Default categories and rules |
