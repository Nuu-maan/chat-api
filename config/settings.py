from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat API"
    
    # Security Settings
    SECRET_KEY: str = "Numankhan007"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Chat Settings
    MAX_MESSAGES_PER_ROOM: int = 100
    TYPING_TIMEOUT_SECONDS: int = 5
    MESSAGE_RETENTION_DAYS: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings() 