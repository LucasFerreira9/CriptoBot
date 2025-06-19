from keras import Model
from keras.layers import LSTM, Dropout, Dense

class LSTM_MODEL1(Model):
    def __init__(self):
        super().__init__()
        self.lstm1 = LSTM(units=128, return_sequences=True)
        self.lstm2 = LSTM(units=64, return_sequences=True)
        self.dropout = Dropout(0.2)
        self.lstm3 = LSTM(units=64, return_sequences=False)
        self.dense = Dense(1, activation="sigmoid")

    def call(self, inputs):
        x = self.lstm1(inputs)
        x = self.lstm2(x)
        x = self.dropout(x)
        x = self.lstm3(x)
        y = self.dense(x)
        return y
    
class LSTM_MODEL2(Model):
    def __init__(self):
        super().__init__()
        self.lstm1 = LSTM(units=64, return_sequences=True)
        self.lstm2 = LSTM(units=64, return_sequences=False)
        self.dense1 = Dense(32, activation="relu")
        self.dense2 = Dense(1,activation="sigmoid")

    def call(self, inputs):
        x = self.lstm1(inputs)
        x = self.lstm2(x)
        x = self.dense1(x)
        y = self.dense2(x)
        return y  


