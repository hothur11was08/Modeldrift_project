from pydantic import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    tf_serving_url: str = "http://tfserving:8501/v1/models/credit_model:predict"
    db_url: str = "postgresql+psycopg2://credit_user:credit_pass@postgres:5432/credit"
    preprocess_path: str = "artifacts/preprocess.pkl"
    model_metrics_path: str = "models/metrics.json"
    drift_reports_dir: str = "drift_reports"
    drift_threshold_psi: float = 0.2

    class Config:
        env_file = ".env"

settings = Settings()

