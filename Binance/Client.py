from typing import Literal, Tuple
from binance.client import Client
from binance.enums import *
import pandas as pd

type Interval = Literal["15m","30m","1h"]

class BinanceClient:
    def __init__(self,api_key,secret_key):
        self.client = Client(api_key, secret_key)

    def isPositioned(self, operated_code:str):
        asset, _ = self.separete_symbol(operated_code)
        balance = self.get_asset_balance(asset)
        minQty = self.get_operation_minQty(operated_code=operated_code)
        return float(balance["free"]) > minQty

    def get_operation_stepSize(self, operated_code:str)->float:
        symbol_info = self.client.get_symbol_info(operated_code)
        lot_size_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
        step_size = float(lot_size_filter['stepSize'])
        return step_size
    
    def get_operation_minQty(self, operated_code:str):
        symbol_info = self.client.get_symbol_info(operated_code)
        lot_size_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
        return float(lot_size_filter["minQty"])
    
    def get_code_price(self, operated_code:str)->float:
        ticker = self.client.get_symbol_ticker(symbol=operated_code)
        return float(ticker["price"])

    def get_asset_balance(self,operated_asset:str)->dict[str,str]:
        """Returns account asset information {asset: code, free: value, locked: value}"""
        balances = self.client.get_account()["balances"]
        for asset in balances:
            if(asset["asset"] == operated_asset):
                return asset
        return None
    
    def separete_symbol(self,symbol: str)->Tuple[str,str]:
    
        quote_assets = ["USDT", "BTC", "ETH", "BNB", "BUSD", "BRL", "EUR"]
    
        for quote in quote_assets:
            if symbol.endswith(quote): 
                asset = symbol.replace(quote,"")
                return asset,quote
            
        return None, None  
    
    def buy_asset_by_percentage(self,percentage: float, operated_code:str):
        _,quote = self.separete_symbol(symbol=operated_code)
        balance = self.get_asset_balance(quote)
        quote_value = percentage * float(balance["free"])
        self.buy_asset(
            quote_value=quote_value, 
            operated_code=operated_code
        )
    
    def buy_asset(self,quote_value:float, operated_code:str):
        current_price = self.get_code_price(operated_code)
        _,quote = self.separete_symbol(symbol=operated_code)
        balance = float(self.get_asset_balance(quote)["free"])

        if(balance < quote_value):
            raise Exception(f"Cannot buy {operated_code}. current balance: {balance} < value: {quote_value}")

        stepSize = self.get_operation_stepSize(operated_code)
        quantity = ((quote_value / current_price) // stepSize) * stepSize

        minQty = self.get_operation_minQty(operated_code)
        if(quantity < minQty):
            raise Exception(f"Cannot buy less than {minQty} in operation: {operated_code}. Requested: {quantity}")

        order = self.client.create_order(
            symbol = operated_code,
            side = SIDE_BUY,
            type = ORDER_TYPE_MARKET,
            quantity = quantity
        )
        print(f"Ativo comprado! Detalhes da transação: {order}")

    def sell_asset(self, operated_code:str):
        "sells all balance"
        asset, _ = self.separete_symbol(operated_code)
        balance = self.get_asset_balance(asset)
        quantity = float(balance["free"])
        stepSize = self.get_operation_stepSize(operated_code)
        quantity = (quantity // stepSize) * stepSize

        minQty = self.get_operation_minQty(operated_code)
        if(quantity < minQty):
            raise Exception(f"Cannot sell less than {minQty} in operation: {operated_code}. Requested: {quantity}")

        order = self.client.create_order(
            symbol = operated_code,
            side = SIDE_SELL,
            type = ORDER_TYPE_MARKET,
            quantity = quantity
        )
            
        print(f"Ativo vendido! Dados da transação: {order}")

    def get_data(self,operated_code:str, interval:str):
        candles = self.client.get_klines(symbol = operated_code, interval = interval, limit = 1000)
        prices = pd.DataFrame(candles)
        prices.columns = ["tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume", "tempo_fechamento", "moedas_negociadas", "numero_trades",
                    "volume_ativo_base_compra", "volume_ativo_cotação", "-"]
        prices = prices[["fechamento", "tempo_fechamento"]]
        prices["tempo_fechamento"] = pd.to_datetime(prices["tempo_fechamento"], unit = "ms").dt.tz_localize("UTC")
        prices["tempo_fechamento"] = prices["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")

        return prices
    
    def get_klines(self,symbol: str, interval: Interval, limit:int):
        if(limit>1000):
            raise Exception(f"Limit exceeded limit of 1000, received: ${limit}")

        return self.client.get_klines(symbol = symbol, interval = interval, limit = limit)
    
    