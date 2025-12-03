# src/train.py
import os, pickle
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Load dataset (no header)
df = pd.read_csv("data/german.data", sep=" ", header=None)

# Assign column names (20 features + 1 target)
columns = [
    "account_status","months","credit_history","purpose","credit_amount","savings",
    "employment","installment_rate","personal_status","guarantors","residence",
    "property","age","other_installments","housing","credit_cards","job",
    "dependents","phone","foreign_worker","target"
]
df.columns = columns

# Define categorical and numeric columns
categorical = ["account_status","credit_history","purpose","savings","employment",
               "personal_status","guarantors","property","other_installments",
               "housing","job","phone","foreign_worker"]
numeric = ["months","credit_amount","installment_rate","residence","age","credit_cards","dependents"]

# Build preprocessor
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", StandardScaler(), numeric)
])

# Fit preprocessor on features (drop target)
X = df.drop(columns=["target"])
preprocessor.fit(X)

# Save fitted preprocessor
os.makedirs("artifacts", exist_ok=True)
with open("artifacts/preprocess.pkl", "wb") as f:
    pickle.dump(preprocessor, f)

