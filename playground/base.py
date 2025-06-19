import pandas as pd
import os 
import time 
from binance.client import Client
from binance.enums import *

from dotenv import load_dotenv

from Binance.Client import BinanceClient
from util import truncate_float
load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

binance_client = Client(api_key, secret_key)

# symbol_info = binance_client.get_symbol_info('BTCUSDT')
# lot_size_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
# min_qty = float(lot_size_filter['minQty'])
# max_qty = float(lot_size_filter['maxQty'])
# step_size = float(lot_size_filter['stepSize'])

# print(lot_size_filter, min_qty, max_qty, step_size)

operated_code = "SOLBRL"
operated_asset = "SOL"
periodo_candle = Client.KLINE_INTERVAL_1HOUR
quantidade = 0.015
large_window = 40
small_window = 7

def get_data(codigo, intervalo):

    candles = binance_client.get_klines(symbol = codigo, interval = intervalo, limit = 1000)
    precos = pd.DataFrame(candles)
    precos.columns = ["tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume", "tempo_fechamento", "moedas_negociadas", "numero_trades",
                    "volume_ativo_base_compra", "volume_ativo_cotação", "-"]
    precos = precos[["fechamento", "tempo_fechamento"]]
    precos["tempo_fechamento"] = pd.to_datetime(precos["tempo_fechamento"], unit = "ms").dt.tz_localize("UTC")
    precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")

    return precos


def run_trading(dados, codigo_ativo, operated_asset, quantidade, posicao):

    dados["media_rapida"] = dados["fechamento"].rolling(window = small_window).mean()
    dados["media_devagar"] = dados["fechamento"].rolling(window = large_window).mean()

    #calculating fast moving average and slow moving average
    last_FMA = dados["media_rapida"].iloc[-1]
    last_SMA = dados["media_devagar"].iloc[-1]

    print(f"Última Média Rápida: {last_FMA} | Última Média Devagar: {last_SMA}")

    conta = binance_client.get_account()

    for ativo in conta["balances"]:
        if ativo["asset"] == operated_asset:
            current_quantity = float(ativo["free"])

    if last_FMA > last_SMA:

        if posicao == False:

            order = binance_client.create_order(
                symbol = codigo_ativo,
                side = SIDE_BUY,
                type = ORDER_TYPE_MARKET,
                quantity = quantidade
            )
            
            print(f"Ativo comprado! Dados da transação: {order}")

            posicao = True

    elif last_FMA < last_SMA:

        if posicao == True:

            order = binance_client.create_order(
                symbol = codigo_ativo,
                side = SIDE_SELL,
                type = ORDER_TYPE_MARKET,
                quantity = truncate_float(current_quantity,3)
            )
            
            print(f"Ativo vendido! Dados da transação: {order}")

            posicao = False

    return posicao


c = BinanceClient(api_key, secret_key)
print(c.get_operation_minQty(operated_code))
exit()

current_position = True

while True:
    dados_atualizados = get_data(
        codigo=operated_code, 
        intervalo=periodo_candle
    )
    current_position = run_trading(
        dados_atualizados, 
        codigo_ativo=operated_code, 
        operated_asset=operated_asset, 
        quantidade=quantidade, 
        posicao=current_position
    )
    time.sleep(60*60)



