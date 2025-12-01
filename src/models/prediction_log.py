from sqlalchemy import Column, Integer, Float, String, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    credit_amount = Column(Float)
    duration = Column(Integer)
    purpose = Column(String)
    housing = Column(String)
    job = Column(String)
    prediction = Column(Integer)
    probability = Column(Float)
    timestamp = Column(TIMESTAMP)

