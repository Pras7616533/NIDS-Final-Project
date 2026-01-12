import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split

# ================================
# Load Preprocessed Data
# ================================

X = np.load("data/processed/X.npy")
y = np.load("data/processed/y.npy")

# ================================
# Use ONLY Normal Traffic for Training
# label 0 = normal, 1 = attack
# ================================

X_normal = X[y == 0]

# Train / Validation split
X_train, X_val = train_test_split(
    X_normal, test_size=0.15, random_state=42
)

# ================================
# Build Autoencoder
# ================================

input_dim = X_train.shape[1]
input_layer = Input(shape=(input_dim,))

# Encoder
encoded = Dense(64, activation='relu')(input_layer)
encoded = Dense(32, activation='relu')(encoded)
encoded = Dense(16, activation='relu')(encoded)

# Decoder
decoded = Dense(32, activation='relu')(encoded)
decoded = Dense(64, activation='relu')(decoded)
decoded = Dense(input_dim, activation='linear')(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

autoencoder.compile(
    optimizer='adam',
    loss='mse'
)

autoencoder.summary()

# ================================
# Train Autoencoder
# ================================

autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=256,
    validation_data=(X_val, X_val),
    callbacks=[EarlyStopping(patience=5, restore_best_weights=True)]
)

# ================================
# Save Model
# ================================

autoencoder.save("models/deepnids_autoencoder.h5")

print("✅ Autoencoder Training Completed")
