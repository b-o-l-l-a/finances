"""Seed data for initial category structure and rules."""

from finances.database import SessionLocal
from finances.models import Category, CategoryRule


DEFAULT_CATEGORIES = {
    "Expenses": {
        "Bills": {
            "Credit Card": {},
            "Electric": {},
            "Home Equity Loan": {},
            "Insurance (Auto)": {},
            "Medical": {},
            "Mortgage": {},
            "Phone": {},
            "Trash & Recycling": {},
            "Water": {},
            "Wifi": {},
        },
        "Food & Drink": {
            "Bar": {},
            "Cannabis": {},
            "Coffee": {},
            "Groceries": {},
            "Restaurants": {},
        },
        "Shopping": {
            "Athletics": {},
            "Clothes": {},
            "Personal": {},
        },
        "Subscriptions": {
            "Technology": {},
        },
        "Transportation": {
            "Car Maintenance": {},
            "Car Payment": {},
            "Gasoline": {},
            "Parking": {},
            "Public Transport": {},
        },
        "Travel": {
            "Expenditures": {},
            "Flights": {},
            "Lodging": {},
        },
        "Fitness": {
            "Equipment": {},
            "Gyms": {},
            "Supplements": {},
        },
        "Hobbies & Entertainment": {
            "Experiences": {},
        },
        "ATM Withdrawal": {},
        "Mammal (Expenses)": {
            "Incidentals": {},
            "Research & Development": {},
            "Supplies": {},
        },
        "Home": {
            "Home Cleaning": {},
            "Home Insurance": {},
            "Home Supplies": {},
            "Repairs": {},
            "Yard": {},
        },
        "Unknown/Uncategorized": {},
    },
    "Income": {
        "Mammal (Income)": {},
        "Miscellaneous Income": {},
        "Payroll": {},
        "Rent": {},
    },
}


# Rules: list of (pattern, category, min_amount, max_amount)
# min_amount is inclusive (>=), max_amount is exclusive (<)
# None means no condition
DEFAULT_RULES = [
    # ATM Withdrawal
    ("atm rebate", "ATM Withdrawal", None, None),
    ("pai atm", "ATM Withdrawal", None, None),
    # Athletics
    ("origin bjj llc", "Athletics", None, None),
    ("scorpion", "Athletics", None, None),
    # Bar
    ("denver beer co", "Bar", None, None),
    ("labates liquors", "Bar", None, None),
    ("mccoys watering", "Bar", None, None),
    ("steep brewing", "Bar", None, None),
    # Car Maintenance
    ("big jims wash", "Car Maintenance", None, None),
    ("chevrolet", "Car Maintenance", None, None),
    ("city wash solutions", "Car Maintenance", None, None),
    ("colorado car wash", "Car Maintenance", None, None),
    ("safelite", "Car Maintenance", None, None),
    # Car Payment
    ("metrum community", "Car Payment", None, None),
    ("metrum community mccu", "Car Payment", None, None),
    # Clothes
    ("the reshop stores", "Clothes", None, None),
    ("west orange hs", "Clothes", None, None),
    # Coffee
    ("coffee", "Coffee", None, None),
    ("dunkin", "Coffee", None, None),
    ("dunkin donuts", "Coffee", None, None),
    ("ewr world bean", "Coffee", None, None),
    ("frothy cup", "Coffee", None, None),
    ("hearth denver", "Coffee", None, None),
    ("la dolce vita", "Coffee", None, None),
    ("la dulce gracia", "Coffee", None, None),
    ("loaded joe", "Coffee", None, 10),
    ("maci cafe", "Coffee", None, None),
    ("pour la france", "Coffee", None, None),
    # Credit Card
    ("usaa credit card payment", "Credit Card", None, None),
    # Electric
    ("xcel energy", "Electric", None, None),
    # Equipment
    ("road runne", "Equipment", None, None),
    # Expenditures
    ("yellowstone", "Expenditures", None, None),
    # Experiences
    ("marcelogarciastore", "Experiences", None, None),
    # Flights
    ("dtcom dallas", "Flights", None, None),
    ("frontier airlines", "Flights", None, None),
    ("priceln*frontier", "Flights", None, None),
    ("united airlines", "Flights", None, None),
    # Food & Drink (amount-conditional)
    ("7-eleven", "Food & Drink", None, 20),
    ("7-eleven", "Gasoline", 20, None),
    # Gasoline
    ("afmzs", "Gasoline", None, None),
    ("circle", "Gasoline", None, None),
    ("loaf n", "Gasoline", None, None),
    ("phillips 66", "Gasoline", None, None),
    # Groceries
    ("city-market", "Groceries", None, None),
    ("cvs/pharmacy", "Groceries", None, None),
    ("instacart", "Groceries", None, None),
    ("king soopers", "Groceries", None, None),
    ("safeway", "Groceries", None, None),
    ("sprouts", "Groceries", None, None),
    ("tst fresh", "Groceries", None, None),
    ("vending machine", "Groceries", None, None),
    ("walgreens", "Groceries", None, None),
    # Gyms
    ("crossfit", "Gyms", None, None),
    ("portal thermaculture", "Gyms", None, None),
    ("shogun", "Gyms", None, None),
    ("shogun jiu jitsu", "Gyms", None, None),
    ("wtfboxing", "Gyms", None, None),
    ("yoga box", "Gyms", None, None),
    # Hobbies & Entertainment
    ("comedy works", "Hobbies & Entertainment", None, None),
    ("high country gen", "Hobbies & Entertainment", None, None),
    ("ikon pass", "Hobbies & Entertainment", None, None),
    ("snow.com", "Hobbies & Entertainment", None, None),
    ("ticket", "Hobbies & Entertainment", None, None),
    ("ticketscentr", "Hobbies & Entertainment", None, None),
    # Home
    ("vectra mechanical", "Home", None, None),
    # Home Cleaning
    ("less stress home", "Home Cleaning", None, None),
    # Home Equity Loan
    ("rocket mortgage", "Home Equity Loan", 550, 551),
    # Home Insurance
    ("usaa", "Home Insurance", 163, 168),
    # Home Supplies
    ("blueair", "Home Supplies", None, None),
    ("lowe s", "Home Supplies", None, None),
    # Incidentals
    ("fedex", "Incidentals", None, None),
    ("the ups", "Incidentals", None, None),
    ("usps", "Incidentals", None, None),
    # Income
    ("interest", "Income", None, None),
    # Insurance (Auto)
    ("usaa p&c", "Insurance (Auto)", None, None),
    # Lodging
    ("booking.com", "Lodging", None, None),
    ("christie lodge", "Lodging", None, None),
    ("holiday inn", "Lodging", None, None),
    ("king hotel", "Lodging", None, None),
    ("outdoorsy", "Lodging", None, None),
    # Mammal (Expenses)
    ("claude ai subscr", "Mammal (Expenses)", None, None),
    ("green space", "Mammal (Expenses)", None, None),
    ("selfpublishing", "Mammal (Expenses)", None, None),
    ("veed limited", "Mammal (Expenses)", None, None),
    # Mammal (Income)
    ("mercor io", "Mammal (Income)", None, None),
    # Medical
    ("best in sight", "Medical", None, None),
    ("hydrateivbar", "Medical", None, None),
    ("kaiser", "Medical", None, None),
    ("kimberly garrison", "Medical", None, None),
    # Miscellaneous Income
    ("deposit@mobile", "Miscellaneous Income", None, None),
    # Mortgage
    ("mr.cooper", "Mortgage", None, None),
    ("rocket mortgage", "Mortgage", 1000, None),
    # Parking
    ("laz parking", "Parking", None, None),
    ("rei surface lots", "Parking", None, None),
    ("vail parking", "Parking", None, None),
    ("vail-parking", "Parking", None, None),
    # Payroll
    ("trinet", "Payroll", None, None),
    # Phone
    ("vzwrlss", "Phone", None, None),
    # Public Transport
    ("mta", "Public Transport", None, None),
    ("njt", "Public Transport", None, None),
    ("rtd", "Public Transport", None, None),
    # Repairs
    ("ace hdwe", "Repairs", None, None),
    ("jif plumbing", "Repairs", None, None),
    ("window world", "Repairs", None, None),
    # Research & Development
    ("cu law", "Research & Development", None, None),
    ("eatingpolicy", "Research & Development", None, None),
    ("reciprocity", "Research & Development", None, None),
    # Restaurants
    ("aquavit", "Restaurants", None, None),
    ("arapahoe basin f & b", "Restaurants", None, None),
    ("armk", "Restaurants", None, None),
    ("black diamond grille", "Restaurants", None, None),
    ("bonsignour new york ny", "Restaurants", None, None),
    ("capitol pizza", "Restaurants", None, None),
    ("chavelas", "Restaurants", None, None),
    ("chipotle", "Restaurants", None, None),
    ("dave's bbq", "Restaurants", None, None),
    ("delicatessen", "Restaurants", None, None),
    ("doordash", "Restaurants", None, None),
    ("georges cafe", "Restaurants", None, None),
    ("half moon empanadas", "Restaurants", None, None),
    ("las delicias", "Restaurants", None, None),
    ("loaded joe", "Restaurants", 10, None),
    ("los tacos", "Restaurants", None, None),
    ("lunchboxx", "Restaurants", None, None),
    ("mcdonald", "Restaurants", None, None),
    ("mcdonald's", "Restaurants", None, None),
    ("mead st station", "Restaurants", None, None),
    ("moose jaw", "Restaurants", None, None),
    ("mr egg", "Restaurants", None, None),
    ("rosenberg", "Restaurants", None, None),
    ("shake shack", "Restaurants", None, None),
    ("sushi den", "Restaurants", None, None),
    ("tst smok", "Restaurants", None, None),
    ("twin star", "Restaurants", None, None),
    ("wawa", "Restaurants", None, None),
    ("wendys", "Restaurants", None, None),
    ("wings food", "Restaurants", None, None),
    # Shopping
    ("amazon", "Shopping", None, None),
    ("black diamond denver", "Shopping", None, None),
    ("nike", "Shopping", None, None),
    ("rei #", "Shopping", None, None),
    ("rei.com", "Shopping", None, None),
    ("scheels", "Shopping", None, None),
    ("stiomountain", "Shopping", None, None),
    ("target", "Shopping", None, None),
    # Subscriptions
    ("adobe", "Subscriptions", None, None),
    ("apple", "Subscriptions", None, None),
    ("apple.com/bill", "Subscriptions", None, None),
    ("audible", "Subscriptions", None, None),
    ("canva", "Subscriptions", None, None),
    ("descript", "Subscriptions", None, None),
    ("disney plus", "Subscriptions", None, None),
    ("google", "Subscriptions", None, 10),
    ("google *google one", "Subscriptions", None, None),
    ("hbomax", "Subscriptions", None, None),
    ("hulu", "Subscriptions", None, None),
    ("linkedinprec", "Subscriptions", None, None),
    ("microsoft", "Subscriptions", None, None),
    ("microsoft*microsoft", "Subscriptions", None, None),
    ("netflix", "Subscriptions", None, None),
    ("onxmaps", "Subscriptions", None, None),
    ("prime video", "Subscriptions", None, None),
    ("redcircle", "Subscriptions", None, None),
    ("rocket money", "Subscriptions", None, 10),
    ("rocket money premium", "Subscriptions", None, None),
    ("spotify", "Subscriptions", None, None),
    ("the economist", "Subscriptions", None, None),
    # Supplements
    ("jocko fuel", "Supplements", None, None),
    # Supplies
    ("anthropic", "Supplies", None, None),
    ("best buy", "Supplies", None, None),
    # Transportation
    ("e 470", "Transportation", None, None),
    ("lyft", "Transportation", None, None),
    ("rtd denver", "Transportation", None, None),
    # Trash & Recycling
    ("republic services trash", "Trash & Recycling", None, None),
    # Unknown/Uncategorized
    ("late fee", "Unknown/Uncategorized", None, None),
    ("monthly maintenance fee", "Unknown/Uncategorized", None, None),
    # Water
    ("city of thornton utly", "Water", None, None),
    ("opc*adams co pwcm", "Water", None, None),
    # Wifi
    ("lumencenturylink", "Wifi", None, None),
    # Yard
    ("city floral", "Yard", None, None),
    ("resource central", "Yard", None, None),
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