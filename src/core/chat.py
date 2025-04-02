from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from src.models.message import Message
from src.models.chat_room import ChatRoom
from src.models.user import User
from src.services.database import RedisDatabase
from src.utils.helpers import (
    generate_id,
    format_timestamp,
    sanitize_message_content,
    validate_metadata
)
import logging

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, db: RedisDatabase):
        self.db = db

    async def create_room(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> ChatRoom:
        """Create a new chat room"""
        try:
            room = await self.db.create_room(name, metadata)
            logger.info(f"Created chat room: {room.id}")
            return room
        except Exception as e:
            logger.error(f"Failed to create chat room: {e}")
            raise

    async def create_user(self, username: str, metadata: Optional[Dict[str, Any]] = None) -> User:
        """Create a new user"""
        try:
            user = await self.db.create_user(username, metadata)
            logger.info(f"Created user: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def send_message(
        self,
        room_id: str,
        user_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        reply_to: Optional[str] = None
    ) -> Message:
        """Send a message to a chat room"""
        try:
            # Verify room and user exist
            room = await self.get_room(room_id)
            user = await self.get_user(user_id)
            
            if not room:
                raise ValueError(f"Chat room not found: {room_id}")
            if not user:
                raise ValueError(f"User not found: {user_id}")

            # Create and save message
            message = Message(
                room_id=room_id,
                user_id=user_id,
                content=content,
                metadata=metadata or {},
                reply_to=reply_to
            )
            
            success = await self.db.save_message(room_id, message)
            if success:
                logger.info(f"Sent message to room {room_id} from user {user_id}")
                return message
            else:
                raise Exception("Failed to save message")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def get_room_messages(self, room_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a chat room"""
        try:
            messages = await self.db.get_messages(room_id, limit)
            logger.info(f"Retrieved {len(messages)} messages from room {room_id}")
            return messages
        except Exception as e:
            logger.error(f"Failed to get room messages: {e}")
            raise

    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID"""
        try:
            room = await self.db.get_room(room_id)
            if room:
                logger.info(f"Retrieved chat room: {room.id}")
            else:
                logger.warning(f"Chat room not found: {room_id}")
            return room
        except Exception as e:
            logger.error(f"Failed to get chat room: {e}")
            raise

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        try:
            user = await self.db.get_user(user_id)
            if user:
                logger.info(f"Retrieved user: {user.id}")
            else:
                logger.warning(f"User not found: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise 