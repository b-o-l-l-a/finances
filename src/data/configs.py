TXN_DATE_COLNAME = "txn_date"
TXN_DESCRIPTION_COLNAME = "txn_description"
TXN_AMT_COLNAME = "txn_amount"
BANK_COLNAME = "bank"
ID_COLNAME  = "unique_id"
TXN_STRFTIME_FORMAT = "%Y-%m-%d"

usaa_config = {
    "columns" : [
        "status", 
        None,
        TXN_DATE_COLNAME,
        None,
        TXN_DESCRIPTION_COLNAME,
        "categorization",
        TXN_AMT_COLNAME
    ],
    "filter_positives" : True
}

citizens_config = {
    "columns" : [
        "Transaction Type",
        TXN_DATE_COLNAME,
        "Account Type",
        TXN_DESCRIPTION_COLNAME,
        TXN_AMT_COLNAME,
        "Reference No.",
        "Credits",
        "Debits"
    ],
    "filter_positives" : True
}