import numpy
from datetime import datetime

def truncate_float(number, decimals):
    factor = 10 ** decimals
    return int(number * factor) / factor

def create_windows(data:numpy.ndarray, n:int)->numpy.ndarray:
    features = data.shape[-1]
    return data.reshape((-1, n, features))

def timestamp_to_hour(timestamp:int):
    return datetime.fromtimestamp(timestamp / 1000).hour