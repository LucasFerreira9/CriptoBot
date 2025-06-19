from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from time import sleep
import traceback
from Binance.Client import BinanceClient, Interval
from Binance.History import History
from Binance.Strategy import Strategy
import matplotlib.pyplot as plt
import numpy as np

class OnOperationDone(ABC):
    @abstractmethod
    def execute(self, time: str, asset_balance: float, quote_balance: float):
        pass

class TradeRoutine():
    def __init__(self, strategy:Strategy, client: BinanceClient, onOperationDone:OnOperationDone=None):
        self.strategy = strategy 
        self.client = client
        self.onOperationDone = onOperationDone
    
    def __getIntervalValueInMinutes(self, interval:Interval)->int:
        match(interval):
            case "15m": return 15
            case "30m": return 30
            case "1h": return 60

    def start(self):
        interval = self.strategy.interval
        interval_minutes = self.__getIntervalValueInMinutes(interval)
        history = History(self.client,self.strategy.symbol,interval, 1000)

        while(True):
            isPositioned = self.client.isPositioned(self.strategy.symbol)
            try:
                operation_done = False

                if(isPositioned):
                    should_sell = self.strategy.should_sell(history)
                    if(should_sell):
                        self.strategy.sell(self.client)
                        operation_done = True
                else:
                    should_buy = self.strategy.should_buy(history)
                    if(should_buy):
                        self.strategy.buy(self.client)
                        operation_done = True

                if(operation_done and self.onOperationDone!=None):
                    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    asset_code, quote_code = self.client.separete_symbol(self.strategy.symbol)
                    asset_balance = self.client.get_asset_balance(asset_code)["free"]
                    quote_balance = self.client.get_asset_balance(quote_code)["free"]
                    self.onOperationDone.execute(time, asset_balance, quote_balance)

                    
            except Exception as e:
                print(e)
                traceback.print_exc()

            sleep(60 * interval_minutes)

    # Used for backtesting 
    def backtest(self,start_from:int, initial_balance:float):
        history = History(self.client, self.strategy.symbol, self.strategy.interval, 1000)
        
        balances = [initial_balance]
        assets_balances = [0]
        isPositioned = False
        
        for time_index in range(start_from, history.limit):
            current_history = deepcopy(history)
            current_history.setDataByHistory(deepcopy(history),0,time_index)
            
            if(isPositioned):
                should_sell = self.strategy.should_sell(current_history)
                if(should_sell):
                    new_asset_balance, new_balance = self.simulate_sell(assets_balances[-1],balances[-1],current_history.close[-1])
                    balances.append(new_balance)
                    assets_balances.append(new_asset_balance)
                    isPositioned = False

            else:
                should_buy = self.strategy.should_buy(current_history)
                if(should_buy):
                    new_asset_balance, new_balance = self.simulate_buy(1,assets_balances[-1],balances[-1],current_history.close[-1])
                    balances.append(new_balance)
                    assets_balances.append(new_asset_balance)
                    isPositioned = True
                    
        
        print(f"initial: ${balances[0]} - final: ${balances[-1]}")
        print(f"initial: ${assets_balances[0]} - final: ${assets_balances[-1]}")
        
        x_values = np.arange(len(balances))

        # Plot the graph
        plt.plot(x_values, balances, marker='o', linestyle='-', color='b', label="Data")

        # Labels and title
        plt.xlabel("Index")
        plt.ylabel("Value")
        plt.title("Line Graph from Array")
        plt.legend()

        # Show the graph
        plt.show()
    
    def simulate_buy(self, percentage, asset_balance, balance, current_price):
        symbol = self.strategy.symbol
        value = percentage * balance

        stepSize = self.client.get_operation_stepSize(symbol)
        quantity = ((value / current_price) // stepSize) * stepSize

        new_asset_balance = asset_balance + quantity
        new_balance = balance - value

        return new_asset_balance, new_balance
    
    def simulate_sell(self, asset_balance, balance, current_price):
        symbol = self.strategy.symbol
        stepSize = self.client.get_operation_stepSize(symbol)
        quantity = (asset_balance // stepSize) * stepSize

        new_asset_balance = asset_balance - quantity
        new_balance = balance + (quantity * current_price)

        return new_asset_balance, new_balance