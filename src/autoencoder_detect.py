import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report

# Load data & model
X = np.load("data/processed/X.npy")
y = np.load("data/processed/y.npy")

model = load_model("models/deepnids_autoencoder.h5")

# Reconstruction error
reconstructions = model.predict(X)
mse = np.mean(np.power(X - reconstructions, 2), axis=1)

# Threshold (tuned empirically)
threshold = np.percentile(mse, 95)

# Anomaly detection
y_pred = (mse > threshold).astype(int)

print("Threshold:", threshold)
print(classification_report(y, y_pred, target_names=["Normal", "Attack"]))
