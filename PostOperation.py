import os
from Binance.TradeRoutine import OnOperationDone
import pandas as pd

class RegisterOperation(OnOperationDone):
    def __init__(self, log_path:str):
        self.log_path = log_path
        if(not os.path.exists(log_path)):
            pd.DataFrame(columns=["time","asset_balance","balance"]).to_csv(log_path, index=False)

        self.df = pd.read_csv(log_path)
        

    def execute(self, time, asset_balance, quote_balance):
        new_row = pd.DataFrame([[time, asset_balance, quote_balance]], columns=["time","asset_balance","balance"])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_csv(self.log_path, index=False)