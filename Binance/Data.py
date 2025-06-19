from datetime import datetime
import math
from Binance.Client import Client
from util import timestamp_to_hour,create_windows

import numpy as np
from sklearn.preprocessing import MinMaxScaler

def get_dataset(client:Client,days:int, symbol,window_size:int=24):
    """
        return x and y
        x=[[close_value, day_hour],,...,v_limit] 
        y=0 for sell time
        y=1 for buy time
    """

    today = timestamp_to_hour(datetime.now().timestamp()*1000)
    last_hours = (24*days) + today + 1
    hour_candles = client.get_klines(symbol = symbol, interval = client.KLINE_INTERVAL_1HOUR, limit = last_hours)
    hour_candles = hour_candles[:-(today+1)]
    
    data = np.array(list(map(lambda moment: [float(moment[4]),timestamp_to_hour(moment[6]),float(moment[2]),float(moment[3])],hour_candles)))
    windows = create_windows(data,24)
   
    index = window_size - 1
    x = []
    y = []
   
    for i in range(index, len(data)):
        window = data[i-index:i+1]
        
        day_index = math.floor(i / 24)
        
        day_window = windows[day_index]
        day_min = day_window[:,0].min()
        day_max = day_window[:,0].max()
        max_distance = day_max-day_min
        
        value = window[-1,0]

        label = (day_max - value) / max_distance

        x.append(window)
        y.append(label)
    
    x = np.array(x)
    y = np.array(y)

    reshaped = x.reshape(-1,x.shape[-1])
    scaler = MinMaxScaler()
    reshaped = scaler.fit_transform(reshaped)
    x = reshaped.reshape(x.shape)

    return x,y

    