import joblib
import requests
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.prediction_log import PredictionLog
from src.config.settings import settings

router = APIRouter()

# ✅ Load preprocessing pipeline once at startup
try:
    preprocess = joblib.load("artifacts/preprocess.pkl")
except Exception as e:
    raise RuntimeError(f"Failed to load preprocessing pipeline: {e}")

# ✅ Define request schema so FastAPI validates input
class PredictRequest(BaseModel):
    purpose: str
    housing: str
    job: str
    age: int
    credit_amount: float
    duration: int

# ✅ Build DB session factory from settings
engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post("/predict")
def predict(request: PredictRequest):
    try:
        # Build DataFrame with correct column names
        df = pd.DataFrame([request.dict()])

        # Transform input
        X = preprocess.transform(df)

        # Send to TensorFlow Serving
        data = {"instances": X.tolist()}
        r = requests.post(settings.tf_serving_url, json=data)
        r.raise_for_status()

        # Extract probability safely
        predictions = r.json().get("predictions")
        if not predictions or not predictions[0]:
            raise HTTPException(status_code=502, detail="Invalid response from model server")

        prob = predictions[0][0]
        prediction = int(prob >= 0.5)

        # Log to Postgres
        db = SessionLocal()
        try:
            log_entry = PredictionLog(
                **request.dict(),
                prediction=prediction,
                probability=prob
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
        finally:
            db.close()

        return {"prediction": prediction, "probability": prob}

    except HTTPException as he:
        # Bubble up FastAPI HTTP errors
        raise he
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

