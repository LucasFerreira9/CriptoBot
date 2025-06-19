from Binance.Client import BinanceClient, Interval
from Binance.History import CandleParam, History
from Binance.Strategy import Strategy

class MobileAverageStrategy(Strategy):
   
    def __init__(self, small_w:int, large_w:int, interval:Interval, symbol:str):
        self.small_w = small_w
        self.large_w = large_w

        self.last_buy = 0
        self.close = float("inf")

        super().__init__(symbol, interval)

    def should_buy(self,history:History)->bool:
        last_FMA, last_SMA = self._get_averages(history)
        return last_FMA > last_SMA
    
    def should_sell(self,history:History)->bool:
        last_FMA, last_SMA = self._get_averages(history)
        return last_FMA < last_SMA 
    
    def buy(self,client):
        client.buy_asset_by_percentage(1,self.symbol)
        self.last_buy = self.close
    
    def sell(self,client):
        client.sell_asset(self.symbol)
    
    def _get_averages(self, history:History)->tuple[float, float]:
        last_FMA = history.get_last_candles(self.small_w, CandleParam.CLOSE).mean()
        last_SMA = history.get_last_candles(self.large_w, CandleParam.CLOSE).mean()
        self.close = history.get_last_candles(1,CandleParam.CLOSE)[0]
        print(f"Última Média Rápida: {last_FMA} | Última Média Devagar: {last_SMA} | Fechamento: {self.close}")
        return last_FMA, last_SMA
