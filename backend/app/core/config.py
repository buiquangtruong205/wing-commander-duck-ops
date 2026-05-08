# Configuration for Wing Commander Duck Ops
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Wing Commander Duck Ops"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Hand Tracking Settings
    MIN_DETECTION_CONFIDENCE: float = 0.7
    MIN_TRACKING_CONFIDENCE: float = 0.5

    class Config:
        env_file = ".env"

settings = Settings()
