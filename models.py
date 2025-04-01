from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    TYPING = "typing"
    READ = "read"

class Message(BaseModel):
    id: str = Field(..., description="Unique message ID")
    chat_id: str = Field(..., description="Chat room ID")
    user_id: str = Field(..., description="User ID who sent the message")
    content: str = Field(..., description="Message content")
    type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = Field(default=None, description="Additional message metadata")
    reply_to: Optional[str] = Field(default=None, description="ID of the message being replied to")

class ChatRoom(BaseModel):
    id: str = Field(..., description="Unique chat room ID")
    name: str = Field(..., description="Chat room name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    participants: List[str] = Field(default_factory=list, description="List of user IDs in the chat")
    is_private: bool = Field(default=False, description="Whether the chat is private")
    metadata: Optional[Dict] = Field(default=None, description="Additional chat room metadata")

class User(BaseModel):
    id: str = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="User email")
    is_active: bool = Field(default=True)
    last_seen: Optional[datetime] = Field(default=None)
    metadata: Optional[Dict] = Field(default=None, description="Additional user metadata")

class ChatResponse(BaseModel):
    messages: List[Message]
    has_more: bool = Field(default=False, description="Whether there are more messages to load")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for pagination")

class TypingStatus(BaseModel):
    user_id: str
    chat_id: str
    is_typing: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow) 