"""Seed data for initial category structure and rules."""

from finances.database import SessionLocal
from finances.models import Category, CategoryRule


DEFAULT_CATEGORIES = {
    "Expenses": {
        "Fixed": {
            "Insurance": {},
        },
        "Food": {
            "Restaurants": {},
            "Groceries": {},
        },
        "Shopping": {},
        "Subscriptions": {},
        "Transportation": {},
        "Fitness": {},
    },
    "Income": {
        "Payroll": {},
    },
}


DEFAULT_RULES = {
    "chipotle": "Restaurants",
    "amazon": "Shopping",
    "nike": "Shopping",
    "rei.com": "Shopping",
    "netflix": "Subscriptions",
    "hbomax": "Subscriptions",
    "canva": "Subscriptions",
    "king soopers": "Groceries",
    "trinet": "Payroll",
    "usaa p&c": "Insurance",
    "yoga box": "Fitness",
    "interest": "Income",
}


def create_categories(parent_id: int | None, structure: dict, db) -> None:
    """Recursively create categories from nested structure."""
    for name, children in structure.items():
        category = Category(name=name, parent_id=parent_id)
        db.add(category)
        db.flush()

        if children:
            create_categories(category.id, children, db)


def seed_categories() -> None:
    """Seed the database with default category structure."""
    db = SessionLocal()
    try:
        create_categories(None, DEFAULT_CATEGORIES, db)
        db.commit()
        print("Categories seeded.")
    finally:
        db.close()


def seed_rules() -> None:
    """Seed default categorization rules."""
    db = SessionLocal()
    try:
        for pattern, category_name in DEFAULT_RULES.items():
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                print(f"  Warning: Category '{category_name}' not found, skipping '{pattern}'")
                continue

            rule = CategoryRule(pattern=pattern, category_id=category.id)
            db.add(rule)

        db.commit()
        print("Rules seeded.")
    finally:
        db.close()


def print_category_tree() -> None:
    """Print the current category hierarchy."""
    db = SessionLocal()
    try:
        def print_tree(parent_id: int | None, indent: int = 0) -> None:
            categories = db.query(Category).filter(
                Category.parent_id == parent_id
            ).order_by(Category.name).all()

            for cat in categories:
                prefix = "  " * indent + ("└── " if indent > 0 else "")
                print(f"{prefix}{cat.name}")
                print_tree(cat.id, indent + 1)

        print_tree(None)
    finally:
        db.close()


def seed_all() -> None:
    """Seed categories and rules."""
    seed_categories()
    seed_rules()
    print("\nCategory structure:")
    print_category_tree()


if __name__ == "__main__":
    seed_all()
