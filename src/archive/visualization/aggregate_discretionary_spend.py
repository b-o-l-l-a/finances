import argparse
import os
import pandas as pd

def aggregate_spend(filepath, metacategory):

    meta_cat_col = "meta_category"
    cat_col = "category"
    amount_col = "Amount"
    spend_df = pd.read_csv(filepath)
    
    spend_df = spend_df[spend_df[meta_cat_col] == metacategory]
    
    print(spend_df.groupby([cat_col])[amount_col].sum().reset_index())

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Aggregates category spend")
    parser.add_argument("filename", 
        help="name of input file")
    parser.add_argument("-r", "--rootpath",
        default=os.path.join(os.getcwd().replace("/src/visualization", ""), "data", "monthly"),
        help="filepath location where filename resides. Defaults to /data/monthly"
    )
    parser.add_argument("-m", "--metacategory",
        help="meta_category to filter",
        default="Discretionary"
    )
    
    args = parser.parse_args()
    
    csv_path = os.path.join(args.rootpath, args.filename)
    aggregate_spend(csv_path, args.metacategory)