from abc import ABC, abstractmethod

from Binance.Client import BinanceClient
from Binance.History import History

class Strategy(ABC):
    def __init__(self, symbol, interval):
        self.symbol = symbol
        self.interval = interval
    
    @abstractmethod
    def should_buy(self,history:History)-> bool:
        pass

    @abstractmethod
    def should_sell(self,history:History)-> bool:
        pass 

    @abstractmethod
    def buy(self,client: BinanceClient):
        pass 

    @abstractmethod
    def sell(self,client: BinanceClient):
        pass
    