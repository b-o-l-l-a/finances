"""Seed data for initial category structure and rules."""

from finances.database import SessionLocal
from finances.models import Category, CategoryRule


DEFAULT_CATEGORIES = {
    "Expenses": {
        "Bills": {
            "Insurance (Auto)": {},
            "Credit Card": {},
            "Electric": {},
            "Home Equity Loan": {},
            "Phone": {},
            "Medical": {},
            "Mortgage": {},
            "Water": {},
            "Wifi": {},
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
            "Car Maintenance": {},
            "Car Payment": {},
            "Gasoline": {},
            "Parking": {},
        },
        "Travel": {
            "Flights": {},
            "Lodging": {},
            "Expenditures": {},
        },
        "Fitness": {
            "Gyms": {},
            "Supplements": {},
            "Equipment": {},
        },
        "Hobbies & Entertainment": {},
        "ATM Withdrawal": {},
        "Mammal (Expenses)": {
            "Research & Development": {},
        },
        "Home": {},
        "Unknown/Uncategorized": {},
    },
    "Income": {
        "Mammal (Income)": {},
        "Payroll": {},
    },
}


# Rules: list of (pattern, category, min_amount, max_amount)
# min_amount is inclusive (>=), max_amount is exclusive (<)
# None means no condition
DEFAULT_RULES = [
    ("amazon", "Shopping", None, None),
    ("nike", "Shopping", None, None),
    ("rei.com", "Shopping", None, None),
    ("trinet", "Payroll", None, None),
    ("usaa p&c", "Insurance (Auto)", None, None),
    ("interest", "Income", None, None),
    # Amount-conditional rules
    ("7-eleven", "Food", None, 20),       # < $20 = Food
    ("7-eleven", "Gasoline", 20, None),   # >= $20 = Gasoline
    ("afmzs", "Gasoline", None, None),
    # Flight rules
    ("united airlines", "Flights", None, None),
    ("frontier airlines", "Flights", None, None),
    ("dtcom dallas", "Flights", None, None),
    # Bar rules
    ("steep brewing", "Bar", None, None),
    ("denver beer co", "Bar", None, None),
    ("labates liquors", "Bar", None, None),
    # Coffee rules
    ("ewr world bean", "Coffee", None, None),
    ("hearth denver", "Coffee", None, None),
    ("la dolce vita", "Coffee", None, None),
    ("la dulce gracia", "Coffee", None, None),
    ("pour la france", "Coffee", None, None),
    # Subscriptions
    ("adobe", "Subscriptions", None, None),
    ("apple.com/bill", "Subscriptions", None, None),
    ("audible", "Subscriptions", None, None),
    ("canva", "Subscriptions", None, None),
    ("descript", "Subscriptions", None, None),
    ("google *google one", "Subscriptions", None, None),
    ("hbomax", "Subscriptions", None, None),
    ("hulu", "Subscriptions", None, None),
    ("linkedinprec", "Subscriptions", None, None),
    ("microsoft*microsoft", "Subscriptions", None, None),
    ("netflix", "Subscriptions", None, None),
    ("prime video", "Subscriptions", None, None),
    ("redcircle", "Subscriptions", None, None),
    ("rocket money premium", "Subscriptions", None, None),
    ("spotify", "Subscriptions", None, None),
    ("the economist", "Subscriptions", None, None),
    # Restaurants
    ("aquavit", "Restaurants", None, None),
    ("black diamond grille", "Restaurants", None, None),
    ("chavelas", "Restaurants", None, None),
    ("chipotle", "Restaurants", None, None),
    ("delicatessen", "Restaurants", None, None),
    ("georges cafe", "Restaurants", None, None),
    ("loaded joe's", "Restaurants", None, None),
    ("mcdonald's", "Restaurants", None, None),
    ("mead st station", "Restaurants", None, None),
    ("mr egg", "Restaurants", None, None),
    ("sushi den", "Restaurants", None, None),
    ("twin star", "Restaurants", None, None),
    ("wendys", "Restaurants", None, None),
    # Groceries
    ("city-market", "Groceries", None, None),
    ("instacart", "Groceries", None, None),
    ("king soopers", "Groceries", None, None),
    ("safeway", "Groceries", None, None),
    ("sprouts", "Groceries", None, None),
    ("walgreens", "Groceries", None, None),
    # Gyms
    ("crossfit", "Gyms", None, None),
    ("portal thermaculture", "Gyms", None, None),
    ("shogun jiu jitsu", "Gyms", None, None),
    ("wtfboxing", "Gyms", None, None),
    ("yoga box", "Gyms", None, None),
    # Supplements
    ("jocko fuel", "Supplements", None, None),
    # Equipment
    ("road runne", "Equipment", None, None),
    # Transportation
    ("lyft", "Transportation", None, None),
    ("rtd denver", "Transportation", None, None),
    ("e 470", "Transportation", None, None),
    ("priceln*frontier", "Flights", None, None),
    # Parking
    ("laz parking", "Parking", None, None),
    ("rei surface lots", "Parking", None, None),
    ("vail-parking", "Parking", None, None),
    # Car Maintenance
    ("big jims wash", "Car Maintenance", None, None),
    ("colorado car wash", "Car Maintenance", None, None),
    ("chevrolet", "Car Maintenance", None, None),
    ("safelite", "Car Maintenance", None, None),
    # Shopping
    ("rei #", "Shopping", None, None),
    ("target", "Shopping", None, None),
    ("scheels", "Shopping", None, None),
    ("stiomountain", "Shopping", None, None),
    ("black diamond denver", "Shopping", None, None),
    # Lodging
    ("booking.com", "Lodging", None, None),
    ("holiday inn", "Lodging", None, None),
    ("christie lodge", "Lodging", None, None),
    ("outdoorsy", "Lodging", None, None),
    ("king hotel", "Lodging", None, None),
    # Travel Expenditures
    ("yellowstone", "Expenditures", None, None),
    # Hobbies & Entertainment
    ("comedy works", "Hobbies & Entertainment", None, None),
    ("high country gen", "Hobbies & Entertainment", None, None),
    ("ikon pass", "Hobbies & Entertainment", None, None),
    ("snow.com", "Hobbies & Entertainment", None, None),
    ("ticketscentr", "Hobbies & Entertainment", None, None),
    # ATM Withdrawal
    ("pai atm", "ATM Withdrawal", None, None),
    ("atm rebate", "ATM Withdrawal", None, None),
    # Credit Card
    ("usaa credit card payment", "Credit Card", None, None),
    # Electric
    ("xcel energy", "Electric", None, None),
    # Phone
    ("vzwrlss", "Phone", None, None),
    # Mortgage
    ("mr.cooper", "Mortgage", None, None),
    ("rocket mortgage", "Mortgage", 1000, None),
    # Home Equity Loan
    ("rocket mortgage", "Home Equity Loan", 550, 551),
    # Car Payment
    ("metrum community mccu", "Car Payment", None, None),
    # Medical
    ("kaiser", "Medical", None, None),
    ("best in sight", "Medical", None, None),
    ("kimberly garrison", "Medical", None, None),
    ("hydrateivbar", "Medical", None, None),
    # Mammal (Expenses)
    ("claude ai subscr", "Mammal (Expenses)", None, None),
    ("green space", "Mammal (Expenses)", None, None),
    ("selfpublishing", "Mammal (Expenses)", None, None),
    ("veed limited", "Mammal (Expenses)", None, None),
    # Research & Development
    ("cu law", "Research & Development", None, None),
    ("reciprocity", "Research & Development", None, None),
    # Home
    ("vectra mechanical", "Home", None, None),
    # Unknown/Uncategorized
    ("late fee", "Unknown/Uncategorized", None, None),
    ("monthly maintenance fee", "Unknown/Uncategorized", None, None),
    # Water
    ("opc*adams co pwcm", "Water", None, None),
    # Wifi
    ("lumencenturylink", "Wifi", None, None),
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
