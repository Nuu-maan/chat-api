from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A real-time chat API built with FastAPI"
    
    # JWT Settings
    SECRET_KEY: str = "Numankhan007"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Chat Settings
    MAX_MESSAGES_PER_ROOM: int = 100
    MESSAGE_EXPIRY_DAYS: int = 30
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Monitoring
    ENABLE_METRICS: bool = True
    
    # Security
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_PING_INTERVAL: int = 20
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from environment variables

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create settings instance
settings = get_settings()

__all__ = ['settings', 'get_settings'] 