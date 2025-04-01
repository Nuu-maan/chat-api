from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
from datetime import datetime
import uuid
from models import Message, MessageType, TypingStatus
from services.database import db

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_chats: Dict[str, Set[str]] = {}  # user_id -> set of chat_ids
        self.chat_users: Dict[str, Set[str]] = {}  # chat_id -> set of user_ids
        self.typing_users: Dict[str, Dict[str, datetime]] = {}  # chat_id -> {user_id: last_typing_time}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_chats[user_id] = set()
        await db.update_user_status(user_id, True)

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_chats:
            for chat_id in self.user_chats[user_id]:
                if chat_id in self.chat_users:
                    self.chat_users[chat_id].discard(user_id)
            del self.user_chats[user_id]
        await db.update_user_status(user_id, False)

    async def join_chat(self, user_id: str, chat_id: str):
        """Add user to a chat room"""
        if user_id not in self.user_chats:
            self.user_chats[user_id] = set()
        if chat_id not in self.chat_users:
            self.chat_users[chat_id] = set()
        
        self.user_chats[user_id].add(chat_id)
        self.chat_users[chat_id].add(user_id)

        # Send system message about user joining
        system_message = Message(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            user_id="system",
            content=f"User {user_id} joined the chat",
            type=MessageType.SYSTEM,
            timestamp=datetime.utcnow()
        )
        await self.broadcast_to_chat(chat_id, system_message)

    async def leave_chat(self, user_id: str, chat_id: str):
        """Remove user from a chat room"""
        if user_id in self.user_chats:
            self.user_chats[user_id].discard(chat_id)
        if chat_id in self.chat_users:
            self.chat_users[chat_id].discard(user_id)

        # Send system message about user leaving
        system_message = Message(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            user_id="system",
            content=f"User {user_id} left the chat",
            type=MessageType.SYSTEM,
            timestamp=datetime.utcnow()
        )
        await self.broadcast_to_chat(chat_id, system_message)

    async def send_personal_message(self, message: str, user_id: str):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast_to_chat(self, chat_id: str, message: Message):
        """Broadcast message to all users in a chat room"""
        if chat_id in self.chat_users:
            message_json = message.json()
            for user_id in self.chat_users[chat_id]:
                if user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(message_json)

    async def handle_typing(self, user_id: str, chat_id: str, is_typing: bool):
        """Handle typing indicators"""
        if chat_id not in self.typing_users:
            self.typing_users[chat_id] = {}

        if is_typing:
            self.typing_users[chat_id][user_id] = datetime.utcnow()
        else:
            self.typing_users[chat_id].pop(user_id, None)

        # Create typing status message
        typing_status = TypingStatus(
            user_id=user_id,
            chat_id=chat_id,
            is_typing=is_typing,
            timestamp=datetime.utcnow()
        )

        # Broadcast typing status to chat room
        await self.broadcast_to_chat(chat_id, typing_status)

    async def cleanup_typing_status(self):
        """Clean up expired typing statuses"""
        current_time = datetime.utcnow()
        for chat_id in list(self.typing_users.keys()):
            expired_users = [
                user_id for user_id, last_typing in self.typing_users[chat_id].items()
                if (current_time - last_typing).total_seconds() > 5
            ]
            for user_id in expired_users:
                await self.handle_typing(user_id, chat_id, False)

# Create a global connection manager instance
manager = ConnectionManager() 