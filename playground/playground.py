import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report

np.random.seed(42)
def generate_data(n_samples=1000):
    data = []
    labels = []
    for _ in range(n_samples):
        day_prices = np.random.uniform(50, 150, 100)  
        current_price = np.random.choice(day_prices)
        min_price = np.min(day_prices)
        max_price = np.max(day_prices)
        
        if current_price == min_price:
            label = 0
        elif current_price == max_price:
            label = 1
        else:
            label = 2

        data.append(np.append(day_prices, current_price))
        labels.append(label)
    return np.array(data), np.array(labels)

X, y = generate_data()

scaler = MinMaxScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], 1), return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # 3 classes: mínimo, máximo, nenhum
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Loss: {loss}, Accuracy: {accuracy}")

y_pred = np.argmax(model.predict(X_test), axis=1)
print(classification_report(y_test, y_pred, target_names=['Min', 'Max', 'None']))
