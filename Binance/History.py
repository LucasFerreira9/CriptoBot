from enum import Enum
from Binance.Client import BinanceClient, Interval
import numpy as np

class CandleParam(Enum):
    HIGH = 2
    LOW = 3
    CLOSE = 4

class History():
    def __init__(self, client:BinanceClient, symbol:str, interval:Interval, limit:int):
        candles = client.get_klines(symbol, interval, limit)
        self.limit = limit
        self.high = np.array(candles)[:,2].astype(float)
        self.low = np.array(candles)[:,3].astype(float)
        self.close = np.array(candles)[:,4].astype(float)

    
    def setDataByHistory(self,history, init:int, end:int):
        self.limit = history.limit
        self.high = np.copy(history.high)[init:end]
        self.low = np.copy(history.low)[init:end]
        self.close = np.copy(history.close)[init:end]

    def get_last_candles(self,n:int, param: CandleParam)->np.ndarray:
        n = min(n, self.limit)

        match(param):
            case CandleParam.HIGH: return self.high[-n:]
            case CandleParam.LOW: return self.low[-n:]
            case CandleParam.CLOSE: return self.close[-n:]



