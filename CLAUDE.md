# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance tracker CLI that aggregates transactions from bank accounts and allows categorization and budget tracking.

## Branch Structure

- **main** - Core CLI, database, and models without any external provider integration
- **integration/plaid** - Plaid integration for bank account linking
- **integration/teller** - Teller.io integration (to be implemented)

## Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run CLI
finances <command>

# Run tests
pytest

# Run single test
pytest tests/test_file.py::test_name
```

### CLI Commands

- `finances init` - Initialize the SQLite database
- `finances accounts` - List connected accounts
- `finances transactions` - List recent transactions
- `finances categories` - List spending categories
- `finances add-category NAME` - Create a spending category
- `finances spending` - Show spending by category for current month

## Architecture

### Core Components

- **cli.py** - Click-based CLI with all user commands. Entry point is `finances.cli:cli`
- **models.py** - SQLAlchemy 2.0 models using `Mapped` type annotations:
  - `Account` - Connected bank accounts with generic credential fields (`external_account_id`, `access_token`)
  - `Transaction` - Normalized transactions from any source (`external_transaction_id` for deduplication)
  - `Category` - Spending categories with optional budgets
- **database.py** - SQLAlchemy engine/session setup. Uses `SessionLocal()` for sessions
- **config.py** - Environment config loaded from `.env` via python-dotenv

### Transaction Amount Convention

- **Negative = expense, positive = income**

### Adding a New Integration

1. Create a new branch from main: `git checkout -b integration/<provider>`
2. Add provider SDK to dependencies in `pyproject.toml`
3. Create `<provider>_service.py` for API interactions
4. Add `link` and `sync` commands to `cli.py`
5. Add provider-specific `TransactionSource` enum value in `models.py`
6. Add provider config to `config.py` and `.env.example`