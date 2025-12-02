# Location: /Users/sureshhothur/credit_project/scripts/train.py

import os
import random
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# =============================================================================
# Training script: saves a FITTED preprocessing transformer to artifacts/preprocess.pkl
# and exports a TensorFlow SavedModel for TF Serving at models/credit_model/1
# =============================================================================

print("Training German Credit model...")

# Seed for reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
tf.random.set_seed(SEED)

# 1) Define schema (must match API PredictInput exactly)
ALL_COLS = [
    "account_status",    # str
    "months",            # int
    "credit_history",    # str
    "purpose",           # str
    "credit_amount",     # float/int
    "savings",           # str
    "employment",        # str
    "installment_rate",  # int
    "personal_status",   # str
    "guarantors",        # str
    "residence",         # int
    "property",          # str
    "age",               # int
    "other_installments",# str
    "housing",           # str
    "credit_cards",      # int
    "job",               # str
    "dependents",        # int
    "phone",             # str
    "foreign_worker",    # str,
    "credit_rating"      # label (1=good, 2=bad)
]

FEATURE_COLS = [
    "account_status","months","credit_history","purpose","credit_amount","savings",
    "employment","installment_rate","personal_status","guarantors","residence",
    "property","age","other_installments","housing","credit_cards","job",
    "dependents","phone","foreign_worker"
]

NUM_COLS = ["months","credit_amount","installment_rate","residence","age","credit_cards","dependents"]
CAT_COLS = [
    "account_status","credit_history","purpose","savings","employment",
    "personal_status","guarantors","property","other_installments",
    "housing","job","phone","foreign_worker"
]

# 2) Load dataset
data_path = "data/german.data"
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Missing dataset at {data_path}. Ensure the file exists.")

df = pd.read_csv(data_path, sep=r"\s+", names=ALL_COLS, header=None)

# 3) Basic cleaning: enforce dtypes and column order
# Cast numeric columns to int (then float where needed)
for c in NUM_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce").astype(int)

# Ensure credit_amount is float (model-friendly)
df["credit_amount"] = df["credit_amount"].astype(float)

# Cast categorical to string
for c in CAT_COLS:
    df[c] = df[c].astype(str)

# Reorder features exactly as API expects
X_df = df[FEATURE_COLS].copy()

# Labels: map 1=Good -> 0, 2=Bad -> 1
y_raw = df["credit_rating"]
y = (y_raw == 2).astype(int).values

# Optional: train/val split for reporting (model trains on full data after fit)
X_train, X_val, y_train, y_val = train_test_split(
    X_df, y, test_size=0.2, random_state=SEED, stratify=y
)

# 4) Build preprocessing pipeline
numeric = Pipeline(steps=[("scaler", StandardScaler())])
categorical = Pipeline(steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric, NUM_COLS),
        ("cat", categorical, CAT_COLS),
    ]
)

# 5) Fit preprocessor on FULL feature DataFrame, then SAVE THE FITTED OBJECT
preprocessor.fit(X_df)

os.makedirs("artifacts", exist_ok=True)
with open("artifacts/preprocess.pkl", "wb") as f:
    pickle.dump(preprocessor, f)

print("Preprocessing pipeline saved to artifacts/preprocess.pkl")

# 6) Transform features for model training
X_processed_train = preprocessor.transform(X_train)
X_processed_val = preprocessor.transform(X_val)

# 7) Build and train TensorFlow model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu", input_shape=(X_processed_train.shape[1],)),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

history = model.fit(
    X_processed_train, y_train,
    epochs=10,
    batch_size=32,
    validation_data=(X_processed_val, y_val),
    verbose=1
)

# 8) Export for TF Serving
export_path = "models/credit_model/1"
os.makedirs(export_path, exist_ok=True)
tf.saved_model.save(model, export_path)
print(f"Model exported to {export_path}")

