import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Conv1D,
    MaxPooling1D, GlobalMaxPooling1D, Reshape
)
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
# Reshape for CNN
# (samples, timesteps, channels)
# ================================

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_val   = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)

# ================================
# Build CNN Model
# ================================

model = Sequential([
    Conv1D(64, kernel_size=3, activation='relu',
           input_shape=(X_train.shape[1], 1)),
    MaxPooling1D(pool_size=2),

    Conv1D(32, kernel_size=3, activation='relu'),
    GlobalMaxPooling1D(),

    Dense(64, activation='relu'),
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
        "models/deepnids_cnn.h5",
        monitor='val_accuracy',
        save_best_only=True
    )
]

# ================================
# Train CNN
# ================================

history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=256,
    validation_data=(X_val, y_val),
    callbacks=callbacks
)

print("✅ CNN Training Completed Successfully")
