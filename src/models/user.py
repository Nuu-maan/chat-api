from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class TypingStatus(str, Enum):
    TYPING = "typing"
    STOPPED = "stopped"

class ChatResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class User(BaseModel):
    id: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "user123",
                "username": "john_doe",
                "created_at": "2023-12-01T12:00:00Z",
                "updated_at": "2023-12-01T12:00:00Z",
                "metadata": {
                    "avatar_url": "https://example.com/avatar.jpg",
                    "status": "online"
                }
            }
        }
    ) 