from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class ChatRoom(BaseModel):
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "general",
                "name": "General Chat",
                "created_at": "2023-12-01T12:00:00Z",
                "updated_at": "2023-12-01T12:00:00Z",
                "metadata": {
                    "description": "General discussion room",
                    "type": "public"
                }
            }
        }
    ) 