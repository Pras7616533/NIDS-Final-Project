import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# ================================
# Load Preprocessed Data
# ================================

X = np.load("data/processed/X.npy")
y = np.load("data/processed/y.npy")

# One-hot encode labels
y = to_categorical(y, num_classes=2)

# Train / Validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

# ================================
# Reshape for LSTM
# (samples, timesteps, features)
# ================================

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_val   = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)

# ================================
# Build LSTM Model
# ================================

model = Sequential([
    LSTM(64, return_sequences=True,
         input_shape=(X_train.shape[1], 1)),
    Dropout(0.3),

    LSTM(32),
    Dropout(0.3),

    Dense(2, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ================================
# Callbacks
# ================================

callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint(
        "models/deepnids_lstm.h5",
        monitor='val_accuracy',
        save_best_only=True
    )
]

# ================================
# Train LSTM
# ================================

history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=256,
    validation_data=(X_val, y_val),
    callbacks=callbacks
)

print("✅ LSTM Training Completed Successfully")
