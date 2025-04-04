from datetime import datetime, timedelta
import json
import uuid
import logging
from typing import List, Optional
from redis.asyncio import Redis
from src.models.chat_room import ChatRoom
from src.models.user import User
from src.models.message import Message
from src.config.settings import get_settings
from .interface import DatabaseInterface

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisDatabase(DatabaseInterface):
    """Redis implementation of the database interface."""
    
    def __init__(self):
        self._client: Optional[Redis] = None
        self._message_expiry = timedelta(days=settings.MESSAGE_EXPIRY_DAYS)
        self._max_messages = settings.MAX_MESSAGES_PER_ROOM
        self._connection_retries = 3
        self._retry_delay = 1  # seconds
        
    @property
    def redis_client(self) -> Optional[Redis]:
        """Get Redis client instance for testing purposes."""
        return self._client

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self._client:
            self._client = await Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.aclose()
            self._client = None
            
    async def _ensure_connection(self) -> None:
        """Ensure Redis connection is established."""
        if not self._client:
            await self.connect()
            
    async def create_room(self, name: str) -> ChatRoom:
        """Create a new chat room."""
        await self._ensure_connection()
        room_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        room = ChatRoom(
            id=room_id,
            name=name,
            created_at=now
        )
        
        # Convert datetime to string for Redis storage
        mapping = {
            "id": room_id,
            "name": name,
            "created_at": now.isoformat()
        }
        
        # Create room hash and add to rooms set
        key = f"room:{room_id}"
        for field, value in mapping.items():
            await self._client.hset(key, field, value)
        await self._client.sadd("rooms", room_id)
        return room
        
    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID."""
        await self._ensure_connection()
        room_data = await self._client.hgetall(f"room:{room_id}")
        
        if not room_data:
            return None
            
        return ChatRoom(
            id=room_data["id"],
            name=room_data["name"],
            created_at=datetime.fromisoformat(room_data["created_at"])
        )
        
    async def get_rooms(self) -> List[ChatRoom]:
        """Get all chat rooms."""
        await self._ensure_connection()
        room_ids = await self._client.smembers("rooms")
        rooms = []
        
        for room_id in room_ids:
            room = await self.get_room(room_id)
            if room:
                rooms.append(room)
                
        return rooms
        
    async def create_user(self, username: str) -> User:
        """Create a new user."""
        await self._ensure_connection()
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user = User(
            id=user_id,
            username=username,
            created_at=now
        )
        
        # Convert datetime to string for Redis storage
        mapping = {
            "id": user_id,
            "username": username,
            "created_at": now.isoformat()
        }
        
        # Create user hash and add to users set
        key = f"user:{user_id}"
        for field, value in mapping.items():
            await self._client.hset(key, field, value)
        await self._client.sadd("users", user_id)
        return user
        
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        await self._ensure_connection()
        user_data = await self._client.hgetall(f"user:{user_id}")
        
        if not user_data:
            return None
            
        return User(
            id=user_data["id"],
            username=user_data["username"],
            created_at=datetime.fromisoformat(user_data["created_at"])
        )
        
    async def get_users(self) -> List[User]:
        """Get all users."""
        await self._ensure_connection()
        user_ids = await self._client.smembers("users")
        users = []
        
        for user_id in user_ids:
            user = await self.get_user(user_id)
            if user:
                users.append(user)
                
        return users
        
    async def save_message(self, message: Message) -> None:
        """Save a message."""
        await self._ensure_connection()
        message_data = message.model_dump()  # Using model_dump instead of dict
        message_data["created_at"] = message.created_at.isoformat()
        message_data["type"] = message.type.value
        
        # Add message to room's message list
        await self._client.lpush(
            f"room:{message.room_id}:messages",
            json.dumps(message_data)
        )
        
        # Trim message list to max size
        await self._client.ltrim(
            f"room:{message.room_id}:messages",
            0,
            self._max_messages - 1
        )
        
        # Set message expiry
        await self._client.expire(
            f"room:{message.room_id}:messages",
            int(self._message_expiry.total_seconds())
        )
        
    async def get_room_messages(self, room_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a room."""
        await self._ensure_connection()
        messages_data = await self._client.lrange(
            f"room:{room_id}:messages",
            0,
            limit - 1
        )
        
        messages = []
        for message_json in messages_data:
            message_data = json.loads(message_json)
            message_data["created_at"] = datetime.fromisoformat(message_data["created_at"])
            messages.append(Message(**message_data))
            
        return messages 