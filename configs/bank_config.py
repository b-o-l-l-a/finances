from shared import txn_date_col_name, txn_description_col_name, txn_amount_col_name

usaa_config = {
    "columns" : {
        0 : "status",
        1 : None,
        2 : txn_date_col_name,
        3 : None,
        4 : txn_description_col_name,
        5 : "categorization",
        6 : txn_amount_col_name
    },
    "txn_amount_positive_bool" : False
}

citizens_config = {
    "columns" : [
        "Transaction Type",
        txn_date_col_name,
        "Account Type",
        txn_description_col_name,
        txn_amount_col_name,
        "Reference No.",
        "Credits",
        "Debits"
    ],
    "filter_positives" : True
}