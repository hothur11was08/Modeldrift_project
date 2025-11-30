import os
import sys
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from src.lib.db import SessionLocal
from src.models.prediction_log import PredictionLog
from scipy.stats import ks_2samp

router = APIRouter()

def compute_drift():
    db = SessionLocal()
    logs = db.execute(select(PredictionLog)).scalars().all()
    db.close()

    if not logs:
        return {"status": "no data", "psi": None, "ks": None}

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

    # PSI (Population Stability Index) for probability
    bins = pd.qcut(df["probability"], q=10, duplicates="drop")
    actual_dist = df.groupby(bins).size() / len(df)
    expected_dist = [0.1] * len(actual_dist)  # assume uniform expected
    psi = sum((a - e) * np.log((a + 1e-6) / (e + 1e-6)) for a, e in zip(actual_dist, expected_dist))

    # KS test for prediction distribution
    ks_stat, ks_pval = ks_2samp(df["probability"], [0.5] * len(df))

    return {
        "status": "ok",
        "psi": psi,
        "ks_stat": ks_stat,
        "ks_pval": ks_pval,
        "count": len(df)
    }

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
        print("Drift monitoring result:", result)
        sys.exit(0)
    except Exception as e:
        print(f"Drift monitoring failed: {e}")
        sys.exit(1)

