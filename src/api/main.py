# src/api/main.py
import os
import json
import time
import pickle
from typing import Dict, Any, List

import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

# Environment variables
TF_SERVING_URL = os.getenv(
    "TF_SERVING_URL",
    "http://tfserving:8501/v1/models/credit_model:predict"
)
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://credit_user:credit_pass@postgres:5432/credit"
)

# Database engine
engine = create_engine(DB_URL, pool_pre_ping=True)

# Load preprocessing pipeline at startup
PREPROCESS_PATH = os.getenv("PREPROCESS_PATH", "/app/artifacts/preprocess.pkl")
preprocess = None
if os.path.exists(PREPROCESS_PATH):
    with open(PREPROCESS_PATH, "rb") as f:
        preprocess = pickle.load(f)

# FastAPI app
app = FastAPI(title="Credit Risk API", version="1.0.0")


# Input schema: all 20 training columns
class PredictInput(BaseModel):
    account_status: str
    months: int
    credit_history: str
    purpose: str
    credit_amount: float
    savings: str
    employment: str
    installment_rate: int
    personal_status: str
    guarantors: str
    residence: int
    property: str
    age: int
    other_installments: str
    housing: str
    credit_cards: int
    job: str
    dependents: int
    phone: str
    foreign_worker: str


# Output schema
class PredictOutput(BaseModel):
    prediction: float
    model_version: str
    latency_ms: int
    timestamp: str

    # Fix warning about protected namespace
    model_config = {"protected_namespaces": ()}


@app.get("/health")
def health():
    """Basic health check for DB and TF Serving."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "degraded", "db": f"error: {e}"}

    try:
        r = requests.get(TF_SERVING_URL.rsplit(":predict", 1)[0], timeout=2)
        status = r.json()
    except Exception:
        status = {"error": "tfserving_unreachable"}

    return {"status": "ok", "tfserving": status}


def _transform_payload(payload: Dict[str, Any]) -> List[float]:
    """Wrap incoming JSON into DataFrame and transform with preprocessor."""
    if preprocess is None:
        raise HTTPException(status_code=500, detail="Preprocessing pipeline not loaded")

    if not hasattr(preprocess, "transform"):
        raise HTTPException(status_code=500, detail="Preprocessor object is invalid (expected transformer, got array)")

    df = pd.DataFrame([payload])
    transformed = preprocess.transform(df)

    if hasattr(transformed, "toarray"):
        return transformed.toarray()[0].tolist()
    return transformed[0].tolist()


def _insert_prediction(
    conn,
    request_json: str,
    features_vector: str,
    pred_value: float,
    model_version: str,
    latency_ms: int
):
    """Insert prediction record into Postgres."""
    conn.execute(
        text("""
        INSERT INTO predictions (
            timestamp,
            model_version,
            request_json,
            features_vector,
            prediction_value,
            latency_ms
        )
        VALUES (
            NOW(),
            :model_version,
            :request_json,
            :features_vector,
            :prediction_value,
            :latency_ms
        )
        """),
        {
            "model_version": model_version,
            "request_json": request_json,
            "features_vector": features_vector,
            "prediction_value": float(pred_value),
            "latency_ms": int(latency_ms),
        },
    )


@app.post("/v1/predict", response_model=PredictOutput)
def predict(inp: PredictInput):
    """Predict endpoint: transform input, call TF Serving, log to DB."""
    # Transform input
    features = _transform_payload(inp.dict())

    # Call TF Serving
    payload = {"instances": [features]}
    t0 = time.time()
    try:
        resp = requests.post(TF_SERVING_URL, json=payload, timeout=5)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TF Serving unreachable: {e}")

    latency_ms = int((time.time() - t0) * 1000)

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"TF Serving error: {resp.text}")

    j = resp.json()
    try:
        if isinstance(j["predictions"][0], list):
            pred = j["predictions"][0][0]
        else:
            pred = j["predictions"][0]
    except Exception:
        raise HTTPException(status_code=500, detail=f"Invalid TF Serving response: {resp.text}")

    # Get model version
    try:
        status = requests.get(TF_SERVING_URL.rsplit(":predict", 1)[0], timeout=2).json()
        mv = str(status.get("model_version_status", [{}])[0].get("version", "unknown"))
    except Exception:
        mv = "unknown"

    # Log to DB
    try:
        with engine.begin() as conn:
            _insert_prediction(
                conn,
                request_json=json.dumps(inp.dict()),
                features_vector=json.dumps(features),
                pred_value=float(pred),
                model_version=mv,
                latency_ms=latency_ms,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB logging failed: {e}")

    return {
        "prediction": float(pred),
        "model_version": mv,
        "latency_ms": latency_ms,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

