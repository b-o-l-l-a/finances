import git

txn_date_col_name = "txn_date"
txn_description_col_name = "txn_description"
txn_amount_col_name = "txn_amount"
processed_txn_filename = "categorized_txn.csv"
bank_col_name = "bank"
id_col_name = "unique_id"
txn_strftime_format = "%Y-%m-%d"

def get_git_root(path):
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root

data_root_dir = "data"
data_raw_dir = "data/raw"
data_interim_dir = "data/interim"
data_processed_dir = "data/processed"

txn_categorization_config = {
    "type" : ["discretionary", "fixed", "intermittent", "variable"],
    "mapping" : {
        "Auto and Transport" : [
            "Gas", "Insurance", "Lease Payment",
            "Maintenance", "Miscellaneous", "Parking",  "Parts",
            "Public Transport", "Ride Share", "Tolls"
        ], 
        "Bills and Utilities" : [
            "Credit Card Payment", "Energy", "Phone", "Rent", "TV", "Utilities (Energy, TV, Wifi)", "Wifi"
        ],
        "Dining Out" : [
            "Bars", "Coffee", "Group", "Solo"
        ],
        "Education" : [
            "Student Loan Payment",
            "Miscellaneous",
            "Tuition"
        ],
        "Experiences" : [
            "Flight", "Group", "Hobbies", "Lodging", "Tickets"
        ],
        "Entertainment" : [
            "Audible", "Amazon Prime", "Other", "Sports", "Spotify", "TV"
        ],
        "Fees and Charges" : [
            "Bank Service Fee", "Late Fee"
        ],
        "Gifts and Donations" : [
            "Charity", "Holiday/Birthday", "Political", "Other"
        ],
        "Groceries" : [
            "Combo", "Food", "Non-Food", "Unknown"
        ],
        "Health and Fitness" : [
            "Gym", "Medical Care", "Body Maintenance", "Miscellaneous" , "Therapist", "Yoga"
        ], 
        "Hobbies" : [
            "MTB", "Other"
            "Snowboarding - Gear", "Snowboarding - Miscellaneous", "Snowboarding - Pass"
        ],
        "Income" : [
            "Gift", "Lyft", "Other", "Oracle"
        ],
        "Investments" : [
            "Investment - Withdrawal", "Investment - Deposit"
        ],
        "Miscellaneous" : ["Shipping", "Tools", "Wifi"],
        "Personal Care" : [
            "Drycleaning", "Haircut", "Laundry"
        ],
        "Shopping" : [
            "Clothes", "Gear", "Alcohol", "Technology"
        ], 
        "Taxes" : [
            "Taxes - Federal", "Taxes - State", "Taxes - Local"
        ],
        "Uncategorized" : [
            "ATM Withdrawal", "Bank Transfer", "Credit Card Redemption" , "Other"
        ],
        "Vanlife" : [
            "Accessories", "Auto Parts", "Gym", "Loan Payment", "Maintenance", "PO Box", "Storage"
        ]
    }
}