from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "neuroflow"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "neuroflow"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    REDIS_PASSWORD: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    LLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()