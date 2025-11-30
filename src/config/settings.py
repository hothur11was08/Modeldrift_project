from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    db_url: str  # will be injected from Docker Compose (DB_URL)
    tf_serving_url: str  # will be injected from Docker Compose (TF_SERVING_URL)

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

