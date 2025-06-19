from dotenv import load_dotenv
from Binance.TradeRoutine import TradeRoutine
from PostOperation import RegisterOperation
from Strategies import MobileAverageStrategy
from Binance.Client import BinanceClient
from binance.enums import *
import os

load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

client = BinanceClient(api_key, secret_key)

strategy = MobileAverageStrategy(
    small_w=7,
    large_w=40,
    interval=KLINE_INTERVAL_1DAY,
    symbol="SOLBRL",
)

tradeRoutine = TradeRoutine(
    strategy=strategy, 
    client=client, 
    onOperationDone=RegisterOperation("logs.csv")
)
#tradeRoutine.start()

tradeRoutine.backtest(31,100)
