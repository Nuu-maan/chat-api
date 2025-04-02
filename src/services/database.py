from typing import List, Optional, Dict, Any, AsyncIterator
import json
from datetime import datetime, timedelta
import redis.asyncio as redis
from src.config.settings import get_settings
from src.models.message import Message, MessageType
from src.models.chat_room import ChatRoom
from src.models.user import User
import asyncio
import logging
from redis.exceptions import ConnectionError, TimeoutError
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisDatabase:
    def __init__(self):
        self.redis_client = None
        self.message_expiry = timedelta(days=settings.MESSAGE_EXPIRY_DAYS)
        self.max_messages = settings.MAX_MESSAGES_PER_ROOM
        self.connection_retries = 3
        self.retry_delay = 1  # seconds

    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None

    async def create_room(self, name: str) -> ChatRoom:
        """Create a new chat room."""
        try:
            await self.connect()
            room_id = str(uuid.uuid4())
            now = datetime.utcnow()
            room = ChatRoom(
                id=room_id,
                name=name,
                created_at=now,
                updated_at=now
            )
            key = f"room:{room_id}"
            await self.redis_client.hset(key, "id", room_id)
            await self.redis_client.hset(key, "name", name)
            await self.redis_client.hset(key, "created_at", room.created_at.isoformat())
            await self.redis_client.hset(key, "updated_at", room.updated_at.isoformat())
            await self.redis_client.hset(key, "metadata", json.dumps(room.metadata))
            await self.redis_client.sadd("rooms", room_id)
            return room
        except Exception as e:
            logging.error(f"Error creating room: {e}")
            raise

    async def get_rooms(self) -> List[ChatRoom]:
        """Get all chat rooms."""
        try:
            await self.connect()
            room_ids = await self.redis_client.smembers("rooms")
            rooms = []
            for room_id in room_ids:
                room = await self.get_room(room_id)
                if room:
                    rooms.append(room)
            return rooms
        except Exception as e:
            logging.error(f"Error getting rooms: {e}")
            raise

    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID."""
        try:
            await self.connect()
            data = await self.redis_client.hgetall(f"room:{room_id}")
            if not data:
                return None
            return ChatRoom(
                id=data["id"],
                name=data["name"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=json.loads(data["metadata"])
            )
        except Exception as e:
            logging.error(f"Error getting room: {e}")
            raise

    async def create_user(self, username: str) -> User:
        """Create a new user."""
        try:
            await self.connect()
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()
            user = User(
                id=user_id,
                username=username,
                created_at=now,
                updated_at=now
            )
            key = f"user:{user_id}"
            await self.redis_client.hset(key, "id", user_id)
            await self.redis_client.hset(key, "username", username)
            await self.redis_client.hset(key, "created_at", user.created_at.isoformat())
            await self.redis_client.hset(key, "updated_at", user.updated_at.isoformat())
            await self.redis_client.hset(key, "metadata", json.dumps(user.metadata))
            await self.redis_client.sadd("users", user_id)
            return user
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            raise

    async def get_users(self) -> List[User]:
        """Get all users."""
        try:
            await self.connect()
            user_ids = await self.redis_client.smembers("users")
            users = []
            for user_id in user_ids:
                user = await self.get_user(user_id)
                if user:
                    users.append(user)
            return users
        except Exception as e:
            logging.error(f"Error getting users: {e}")
            raise

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        try:
            await self.connect()
            data = await self.redis_client.hgetall(f"user:{user_id}")
            if not data:
                return None
            return User(
                id=data["id"],
                username=data["username"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=json.loads(data["metadata"])
            )
        except Exception as e:
            logging.error(f"Error getting user: {e}")
            raise

    async def save_message(self, message: Message):
        """Save a message to Redis."""
        try:
            await self.connect()
            key = f"message:{message.id}"
            await self.redis_client.hset(key, "id", message.id)
            await self.redis_client.hset(key, "room_id", message.room_id)
            await self.redis_client.hset(key, "user_id", message.user_id)
            await self.redis_client.hset(key, "content", message.content)
            await self.redis_client.hset(key, "type", message.type)
            await self.redis_client.hset(key, "created_at", message.created_at.isoformat())
            # Add message to room's message list
            await self.redis_client.lpush(f"room:{message.room_id}:messages", message.id)
        except Exception as e:
            logging.error(f"Error saving message: {e}")
            raise

    async def get_room_messages(self, room_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a chat room."""
        try:
            await self.connect()
            message_ids = await self.redis_client.lrange(f"room:{room_id}:messages", 0, limit - 1)
            messages = []
            for msg_id in message_ids:
                data = await self.redis_client.hgetall(f"message:{msg_id}")
                if data:
                    messages.append(Message(
                        id=data["id"],
                        room_id=data["room_id"],
                        user_id=data["user_id"],
                        content=data["content"],
                        type=MessageType(data["type"]),
                        created_at=datetime.fromisoformat(data["created_at"])
                    ))
            return messages
        except Exception as e:
            logging.error(f"Error getting room messages: {e}")
            raise

# Create a singleton instance
db = RedisDatabase()

__all__ = ['db'] 