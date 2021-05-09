class TransactionFile():
    
    def __init__(self, path, file):
        
        self.root_dir = path
        self.file = file
        self.full_path = os.path.join(path, file)
        self.citizens_bank_key = 'citizens'
        self.usaa_bank_key = 'usaa'
        self.fidelity_bank_key = 'fidelity'
        self.discover_key = 'discover'
        
        self.bank = self.get_bank()
        
        if self.bank == self.citizens_bank_key:
            self.bank_config = citizens_config
        elif self.bank == self.usaa_bank_key:
            self.bank_config = usaa_config
            
        self.account_type = self.get_account_type()
        self.txn_df = self.get_txn_df()
        
    def get_bank(self):
        
        if 'bk_download' in self.file:
            bank = self.usaa_bank_key
        elif 'EXPORT' in self.file:
            bank = self.citizens_bank_key
            
        return bank
                 
    def get_account_type(self):

        acceptable_inputs = ['credit', 'checking', 'investment']
        prompt = "What kind of account is this file? {}\nMust be one of {}".format(self.file, acceptable_inputs)
        
        while True:
            acct_type = input(prompt)
            
            if acct_type not in acceptable_inputs:
                print("ERROR! Input not one of {}\n".format(acceptable_inputs))
                continue
            else:
                break
                
        return acct_type
            
    def get_txn_df(self):

        bank = self.bank
        acct_type = self.account_type
        
        header = 0 if self.bank in [self.citizens_bank_key] else None
        raw_txn_df = pd.read_csv(self.full_path, header=header)
        
        columns = self.bank_config['columns']
        filter_positives = self.bank_config['filter_positives']
        raw_txn_df.columns = columns

        txn_df = raw_txn_df[[txn_date_col_name, txn_amount_col_name, txn_description_col_name]].copy()

        txn_df[txn_amount_col_name] = txn_df[txn_amount_col_name].astype(str)
        txn_df[txn_amount_col_name] = txn_df[txn_amount_col_name].str.replace("--", "")
        txn_df[txn_amount_col_name] = txn_df[txn_amount_col_name].astype(float)
        txn_df[txn_date_col_name]= pd.to_datetime(txn_df[txn_date_col_name]) 
        
        txn_df["bank"] = self.bank
        txn_df["acct_type"] = self.account_type
        
        txn_df["unique_id"] = txn_df.apply(
            lambda x:"{}_{}_{}_{}".format(
                bank, 
                acct_type, 
                x[txn_date_col_name].strftime("%Y%m%d"), 
                abs(x[txn_amount_col_name])
            ), axis = 1
        )

        return txn_df
    