from redis.asyncio import Redis
import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from config.settings import settings
from models import Message, ChatRoom, User, MessageType

class RedisDatabase:
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self._connected = False
        self.max_messages = settings.MAX_MESSAGES_PER_ROOM

    async def connect(self):
        """Initialize Redis connection"""
        if not self._connected:
            # Test the connection by sending a ping
            await self.redis.ping()
            self._connected = True

    async def close(self):
        if self._connected:
            await self.redis.close()
            self._connected = False

    async def save_message(self, message: Message) -> None:
        """Save a message to Redis"""
        try:
            # Save message data
            message_data = {
                "id": str(message.id),
                "chat_id": str(message.chat_id),
                "user_id": str(message.user_id),
                "content": message.content or "",
                "type": message.type.value,
                "timestamp": message.timestamp.isoformat(),
                "metadata": json.dumps(message.metadata) if message.metadata else "{}",
                "reply_to": str(message.reply_to) if message.reply_to else ""
            }
            await self.redis.hmset(f"message:{message.id}", message_data)
            
            # Ensure the chat messages key exists as a list
            chat_key = f"chat:{message.chat_id}:messages"
            key_type = await self.redis.type(chat_key)
            
            if key_type != b"list":
                # If the key exists but is not a list, delete it
                await self.redis.delete(chat_key)
            
            # Add to chat history
            await self.redis.lpush(chat_key, str(message.id))
            
            # Trim old messages if needed
            try:
                message_count = await self.redis.llen(chat_key)
                if message_count > settings.MAX_MESSAGES_PER_ROOM:
                    # Remove oldest messages
                    await self.redis.ltrim(chat_key, 0, settings.MAX_MESSAGES_PER_ROOM - 1)
            except Exception as e:
                print(f"Error trimming messages: {e}")
                
        except Exception as e:
            print(f"Error saving message: {e}")
            raise

    async def get_messages(
        self,
        chat_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages for a chat room with pagination"""
        await self.connect()
        key = f"chat:{chat_id}:messages"
        
        if before:
            before_score = before.timestamp()
            message_ids = await self.redis.zrevrangebyscore(
                key, 0, before_score, limit=limit
            )
        else:
            message_ids = await self.redis.zrevrange(key, 0, limit - 1)
        
        messages = []
        for msg_id in message_ids:
            msg_data = await self.redis.hgetall(f"message:{msg_id}")
            if msg_data:
                messages.append(Message(
                    id=msg_data["id"],
                    chat_id=msg_data["chat_id"],
                    user_id=msg_data["user_id"],
                    content=msg_data["content"],
                    type=MessageType(msg_data["type"]),  # Convert string back to enum
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    metadata=json.loads(msg_data["metadata"]),
                    reply_to=msg_data["reply_to"] if msg_data["reply_to"] else None
                ))
        
        return messages

    async def save_chat_room(self, chat_room: ChatRoom) -> None:
        """Save a chat room to Redis"""
        await self.connect()
        chat_data = {
            "id": chat_room.id,
            "name": chat_room.name,
            "created_at": chat_room.created_at.isoformat(),
            "participants": json.dumps(chat_room.participants),
            "is_private": str(chat_room.is_private),
            "metadata": json.dumps(chat_room.metadata or {})
        }
        await self.redis.hmset(f"chat_room:{chat_room.id}", chat_data)

    async def get_chat_room(self, chat_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID"""
        await self.connect()
        data = await self.redis.hgetall(f"chat_room:{chat_id}")
        if not data:
            return None
            
        return ChatRoom(
            id=data["id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            participants=json.loads(data["participants"]),
            is_private=data["is_private"] == "True",
            metadata=json.loads(data["metadata"])
        )

    async def save_user(self, user: User) -> None:
        """Save a user to Redis"""
        await self.connect()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email or "",
            "is_active": str(user.is_active),
            "last_seen": user.last_seen.isoformat() if user.last_seen else "",
            "metadata": json.dumps(user.metadata or {})
        }
        await self.redis.hmset(f"user:{user.id}", user_data)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        await self.connect()
        data = await self.redis.hgetall(f"user:{user_id}")
        if not data:
            return None
            
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"] if data["email"] else None,
            is_active=data["is_active"] == "True",
            last_seen=datetime.fromisoformat(data["last_seen"]) if data["last_seen"] else None,
            metadata=json.loads(data["metadata"])
        )

    async def update_user_status(self, user_id: str, is_online: bool) -> None:
        """Update user online status"""
        await self.connect()
        await self.redis.hset(f"user:{user_id}", "is_active", str(is_online))
        if is_online:
            await self.redis.hset(f"user:{user_id}", "last_seen", datetime.utcnow().isoformat())

# Create a global database instance
db = RedisDatabase() 