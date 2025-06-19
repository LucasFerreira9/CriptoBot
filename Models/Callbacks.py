from keras.callbacks import Callback

class LossEarlyStopping(Callback):
    def __init__(self, patience=5):
        super(LossEarlyStopping, self).__init__()
        self.patience = patience
        self.best_loss = float('inf')
        self.wait = 0

    def on_epoch_end(self, epoch, logs=None):
        current_loss = logs.get('loss')
        if current_loss < self.best_loss:
            self.best_loss = current_loss
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                print(f"Early stopping triggered at epoch {epoch+1}")
                self.model.stop_training = True