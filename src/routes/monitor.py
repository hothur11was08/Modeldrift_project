import os
import sys
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, text, create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings   # <-- use your existing settings
from src.models.prediction_log import PredictionLog
from scipy.stats import ks_2samp
from datetime import datetime

router = APIRouter()

# Build engine + SessionLocal from settings.db_url
engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def compute_drift():
    db = SessionLocal()
    logs = db.execute(select(PredictionLog)).scalars().all()
    db.close()

    if not logs:
        return {"status": "no data", "psi": None, "ks_stat": None, "ks_pval": None, "count": 0}

    # Convert logs to DataFrame
    df = pd.DataFrame([{
        "age": log.age,
        "credit_amount": log.credit_amount,
        "duration": log.duration,
        "purpose": log.purpose,
        "housing": log.housing,
        "job": log.job,
        "prediction": log.prediction,
        "probability": log.probability,
        "timestamp": log.timestamp
    } for log in logs])

    # --- PSI (Population Stability Index) ---
    bins = pd.qcut(df["probability"], q=10, duplicates="drop")
    actual_dist = df.groupby(bins).size() / len(df)
    expected_dist = [0.1] * len(actual_dist)  # uniform baseline
    psi = sum((a - e) * np.log((a + 1e-6) / (e + 1e-6)) for a, e in zip(actual_dist, expected_dist))

    # --- KS test ---
    ks_stat, ks_pval = ks_2samp(df["probability"], [0.5] * len(df))

    # --- Drift severity classification ---
    if psi < 0.1:
        status = "no drift"
    elif psi < 0.25:
        status = "moderate drift"
    else:
        status = "drift detected"

    result = {
        "status": status,
        "psi": float(psi),
        "ks_stat": float(ks_stat),
        "ks_pval": float(ks_pval),
        "count": len(df)
    }

    # --- Persist results into drift_logs table ---
    try:
        db_url = os.getenv("DB_URL", "postgresql://credit_user:credit_pass@postgres:5432/credit")
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO drift_logs (feature, psi, status, created_at) VALUES (:feature, :psi, :status, :created_at)"),
                {"feature": "probability", "psi": result["psi"], "status": result["status"], "created_at": datetime.now()}
            )
    except Exception as e:
        print(f"Warning: failed to persist drift results: {e}")

    return result

@router.get("/drift")
def monitor_drift():
    try:
        return compute_drift()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift monitoring failed: {e}")

# --- Standalone execution for Jenkins ---
if __name__ == "__main__":
    try:
        result = compute_drift()
        print("=== Drift Monitoring Report ===")
        print(f"PSI: {result['psi']:.3f} → {result['status']}")
        print(f"KS Stat: {result['ks_stat']:.3f}, p-value: {result['ks_pval']:.3f}")
        print(f"Sample size: {result['count']}")
        sys.exit(0)
    except Exception as e:
        print(f"Drift monitoring failed: {e}")
        sys.exit(1)

