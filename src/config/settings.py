import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    db_url: str = os.getenv(
        "DB_URL",
        "postgresql://credit_user:credit_pass@postgres:5432/credit"
    )
    tf_serving_url: str = os.getenv(
        "TF_SERVING_URL",
        "http://tfserving:8501/v1/models/credit_model:predict"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

