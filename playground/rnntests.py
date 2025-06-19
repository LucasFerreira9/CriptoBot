from dotenv import load_dotenv
from Binance.Client import BinanceClient
import os
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

from Binance.Data import get_dataset
from Models.RNN import LSTM_MODEL1, LSTM_MODEL2

load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

client = BinanceClient(api_key, secret_key)

def plot_loss(history):
    """
    Plots the training and validation loss from a Keras History object.

    Parameters:
    history (keras.callbacks.History): A History object returned from model.fit().
    """
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    if 'val_loss' in history.history:
        plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Loss Over Epochs')
    plt.legend()
    plt.grid(True)
    plt.show()

x, y = get_dataset(client.client,40,"BTCUSDT",window_size=60)

#simulation

sell_threshold = 0.3
buy_threshold = 0.7
balance = 0.0
initial_balance = balance
pos = False
day = 1
factor = 720
last_spend = 0

model = LSTM_MODEL1()
model.compile(optimizer="rmsprop",loss="mse")

days = [balance]

while(factor+24 < 960):
    x_train = x[:factor]
    x_test = x[factor:factor+24]
    y_train = y[:factor]
    y_test = y[factor:factor+24]

    history = model.fit(x=x_train,y=y_train,epochs=30)

    preds = model.predict(x_test)

    for index,window in enumerate(x_test):
        pred = preds[index]
        if(pos and pred<=sell_threshold and window[-1,0] > last_spend):
            balance += window[-1,0]
            last_spend = 0
            pos = False
        if(not pos and pred >= buy_threshold):
            balance -= window[-1,0]
            last_spend = window[-1,0]
            pos = True

    print(f"day {day}: balance: {balance}")
    factor+=24
    day+=1
    days.append(balance)
    print(days)
    print(pos)

print(f"initial_balance = {initial_balance}\nbalance = {balance}.\n")
print(days)