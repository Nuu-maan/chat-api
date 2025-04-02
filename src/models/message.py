from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    TYPING = "typing"

class Message(BaseModel):
    id: str
    room_id: str
    user_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    reply_to: Optional[str] = None
    type: MessageType = MessageType.TEXT

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "room_id": "general",
                "user_id": "user123",
                "content": "Hello, world!",
                "created_at": "2023-12-01T12:00:00Z",
                "metadata": {"type": "text"},
                "reply_to": None,
                "type": "text"
            }
        } 