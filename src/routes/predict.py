import joblib
import requests
import pandas as pd
from fastapi import APIRouter, HTTPException
from src.lib.db import SessionLocal
from src.models.prediction_log import PredictionLog
from src.config.settings import settings

router = APIRouter()

# Load preprocessing pipeline once at startup
try:
    preprocess = joblib.load("artifacts/preprocess.pkl")
except Exception as e:
    raise RuntimeError(f"Failed to load preprocessing pipeline: {e}")

@router.post("/predict")
def predict(payload: dict):
    try:
        # Build DataFrame with correct column names
        df = pd.DataFrame([{
            "purpose": payload["purpose"],
            "housing": payload["housing"],
            "job": payload["job"],
            "age": payload["age"],
            "credit_amount": payload["credit_amount"],
            "duration": payload["duration"]
        }])

        # Transform input
        X = preprocess.transform(df)

        # Send to TensorFlow Serving
        data = {"instances": X.tolist()}
        r = requests.post(settings.tf_serving_url, json=data)
        r.raise_for_status()

        # Extract probability
        prob = r.json()["predictions"][0][0]
        prediction = int(prob >= 0.5)

        # Log to Postgres
        db = SessionLocal()
        try:
            log_entry = PredictionLog(
                age=payload["age"],
                credit_amount=payload["credit_amount"],
                duration=payload["duration"],
                purpose=payload["purpose"],
                housing=payload["housing"],
                job=payload["job"],
                prediction=prediction,
                probability=prob
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
        finally:
            db.close()

        return {"prediction": prediction, "probability": prob}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

