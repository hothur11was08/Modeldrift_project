# Location: /Users/sureshhothur/credit_project/scripts/train.py

import os
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import joblib

print("Training German Credit model...")

# 1. Load dataset
cols = [
    "account_status", "months", "credit_history", "purpose", "credit_amount", "savings",
    "employment", "installment_rate", "personal_status", "guarantors", "residence",
    "property", "age", "other_installments", "housing", "credit_cards", "job",
    "dependents", "phone", "foreign_worker", "credit_rating"
]

# FIXED: use data/german.data instead of artifacts/german.data
df = pd.read_csv("data/german.data", sep=r"\s+", names=cols, header=None)

X_df = df.drop(columns=["credit_rating"])
y_raw = df["credit_rating"]

# Convert labels: 1=Good → 0, 2=Bad → 1
y = (y_raw == 2).astype(int)

# 2. Preprocess features
categorical_cols = X_df.select_dtypes(include="object").columns.tolist()
numeric_cols = X_df.select_dtypes(include=["int64", "float64"]).columns.tolist()

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", StandardScaler(), numeric_cols)
    ]
)

# Fit and transform
X_processed = preprocessor.fit_transform(X_df)

# Save preprocessing pipeline
os.makedirs("artifacts", exist_ok=True)
joblib.dump(preprocessor, "artifacts/preprocess.pkl")
print("Preprocessing pipeline saved to artifacts/preprocess.pkl")

# 3. Train model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu", input_shape=(X_processed.shape[1],)),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X_processed, y, epochs=10, batch_size=32, validation_split=0.2)

# 4. Export for TF Serving
export_path = "models/credit_model/1"
os.makedirs(export_path, exist_ok=True)
tf.saved_model.save(model, export_path)
print(f"Model exported to {export_path}")

