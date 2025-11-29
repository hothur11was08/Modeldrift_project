import requests
from fastapi import APIRouter
from pydantic import BaseModel
from src.config.settings import settings

router = APIRouter()

class CreditApplication(BaseModel):
    age: int
    credit_amount: float
    duration: int
    purpose: str
    housing: str
    job: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float

@router.post("/predict", response_model=PredictionResponse)
def predict(req: CreditApplication):
    payload = {"instances": [[req.age, req.credit_amount, req.duration,
                              req.purpose, req.housing, req.job]]}
    r = requests.post(settings.tf_serving_url, json=payload, timeout=10)
    r.raise_for_status()
    prob = float(r.json()["predictions"][0][0])
    return PredictionResponse(prediction=int(prob >= 0.5), probability=prob)

