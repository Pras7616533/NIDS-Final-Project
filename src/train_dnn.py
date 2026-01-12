import numpy as np
import pandas as pd
import joblib

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
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

# Train / Validation Split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

# ================================
# Build DNN Model
# ================================

model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),

    Dense(64, activation='relu'),
    Dropout(0.3),

    Dense(32, activation='relu'),
    Dropout(0.2),

    Dense(2, activation='softmax')
])

# Compile model
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
        filepath="models/deepnids_dnn.h5",
        monitor='val_accuracy',
        save_best_only=True
    )
]

# ================================
# Train Model
# ================================

history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=256,
    validation_data=(X_val, y_val),
    callbacks=callbacks
)

print("✅ DNN Training Completed Successfully")
