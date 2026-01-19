"""Seed data for initial category structure and rules."""

from finances.database import SessionLocal
from finances.models import Category, CategoryRule


DEFAULT_CATEGORIES = {
    "Expenses": {
        "Fixed": {
            "Insurance": {},
        },
        "Food & Drink": {
            "Restaurants": {},
            "Groceries": {},
            "Bar": {},
            "Coffee": {},
        },
        "Shopping": {},
        "Subscriptions": {},
        "Transportation": {
            "Gasoline": {},
        },
        "Travel": {
            "Flights": {},
            "Lodging": {},
        },
        "Fitness": {},
        "Entertainment": {},
    },
    "Income": {
        "Payroll": {},
    },
}


# Rules: list of (pattern, category, min_amount, max_amount)
# min_amount is inclusive (>=), max_amount is exclusive (<)
# None means no condition
DEFAULT_RULES = [
    ("chipotle", "Restaurants", None, None),
    ("amazon", "Shopping", None, None),
    ("nike", "Shopping", None, None),
    ("rei.com", "Shopping", None, None),
    ("netflix", "Subscriptions", None, None),
    ("hbomax", "Subscriptions", None, None),
    ("canva", "Subscriptions", None, None),
    ("king soopers", "Groceries", None, None),
    ("trinet", "Payroll", None, None),
    ("usaa p&c", "Insurance", None, None),
    ("yoga box", "Fitness", None, None),
    ("interest", "Income", None, None),
    # Amount-conditional rules
    ("7-eleven", "Food", None, 20),       # < $20 = Food
    ("7-eleven", "Gasoline", 20, None),   # >= $20 = Gasoline
    # Flight rules
    ("united airlines", "Flights", None, None),
    ("frontier airlines", "Flights", None, None),
    # Bar rules
    ("steep brewing", "Bar", None, None),
    ("denver beer co", "Bar", None, None),
    ("labates liquors", "Bar", None, None),
    # Coffee rules
    ("pour la france", "Coffee", None, None),
    ("la dolce vita", "Coffee", None, None),
    ("hearth denver", "Coffee", None, None),
    # Subscriptions
    ("apple.com/bill", "Subscriptions", None, None),
    ("adobe", "Subscriptions", None, None),
    ("audible", "Subscriptions", None, None),
    ("hulu", "Subscriptions", None, None),
    ("google *google one", "Subscriptions", None, None),
    ("microsoft*microsoft", "Subscriptions", None, None),
    ("the economist", "Subscriptions", None, None),
    ("descript", "Subscriptions", None, None),
    ("redcircle", "Subscriptions", None, None),
    # Restaurants
    ("aquavit", "Restaurants", None, None),
    ("sushi den", "Restaurants", None, None),
    ("mead st station", "Restaurants", None, None),
    ("wendys", "Restaurants", None, None),
    ("mr egg", "Restaurants", None, None),
    ("black diamond grille", "Restaurants", None, None),
    ("chavelas", "Restaurants", None, None),
    # Groceries
    ("sprouts", "Groceries", None, None),
    ("city-market", "Groceries", None, None),
    ("instacart", "Groceries", None, None),
    ("walgreens", "Groceries", None, None),
    # Fitness
    ("crossfit", "Fitness", None, None),
    ("shogun jiu jitsu", "Fitness", None, None),
    # Transportation
    ("lyft", "Transportation", None, None),
    ("rtd denver", "Transportation", None, None),
    ("e 470", "Transportation", None, None),
    ("priceln*frontier", "Flights", None, None),
    # Shopping
    ("rei #", "Shopping", None, None),
    ("target", "Shopping", None, None),
    ("scheels", "Shopping", None, None),
    # Lodging
    ("booking.com", "Lodging", None, None),
    ("holiday inn", "Lodging", None, None),
    ("christie lodge", "Lodging", None, None),
]


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
        for pattern, category_name, min_amount, max_amount in DEFAULT_RULES:
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                print(f"  Warning: Category '{category_name}' not found, skipping '{pattern}'")
                continue

            rule = CategoryRule(
                pattern=pattern,
                category_id=category.id,
                min_abs_amount=min_amount,
                max_abs_amount=max_amount
            )
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
