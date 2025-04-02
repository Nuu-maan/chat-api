from fastapi import WebSocket
from typing import Dict, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections by room_id and user_id
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Store user's active rooms
        self.user_rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """Connect a user to a room"""
        try:
            await websocket.accept()
            logger.info(f"Accepting WebSocket connection for user {user_id} in room {room_id}")

            # Initialize room if it doesn't exist
            if room_id not in self.active_connections:
                self.active_connections[room_id] = {}

            # Store the connection
            self.active_connections[room_id][user_id] = websocket

            # Track user's rooms
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = set()
            self.user_rooms[user_id].add(room_id)

            logger.info(f"User {user_id} connected to room {room_id}")
        except Exception as e:
            logger.error(f"Error connecting user {user_id} to room {room_id}: {e}")
            raise

    async def disconnect(self, room_id: str, user_id: str):
        """Disconnect a user from a room"""
        try:
            # Remove from room connections
            if room_id in self.active_connections:
                if user_id in self.active_connections[room_id]:
                    del self.active_connections[room_id][user_id]
                    if not self.active_connections[room_id]:
                        del self.active_connections[room_id]

            # Remove from user's rooms
            if user_id in self.user_rooms:
                self.user_rooms[user_id].discard(room_id)
                if not self.user_rooms[user_id]:
                    del self.user_rooms[user_id]

            # Notify others in the room
            await self.broadcast_to_room(
                room_id,
                {
                    "type": "system",
                    "content": f"User {user_id} left the chat",
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )

            logger.info(f"User {user_id} disconnected from room {room_id}")
        except Exception as e:
            logger.error(f"Error disconnecting user {user_id} from room {room_id}: {e}")

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast a message to all users in a room"""
        if room_id not in self.active_connections:
            return

        # Convert datetime objects to ISO format strings
        if isinstance(message, dict):
            for key, value in message.items():
                if isinstance(value, datetime):
                    message[key] = value.isoformat()
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, datetime):
                            value[k] = v.isoformat()

        message_json = json.dumps(message)
        for user_id, connection in self.active_connections[room_id].items():
            if user_id != exclude_user:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    await self.disconnect(room_id, user_id)

    async def send_personal_message(self, room_id: str, user_id: str, message: dict):
        """Send a message to a specific user in a room"""
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            try:
                await self.active_connections[room_id][user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending personal message to user {user_id}: {e}")
                await self.disconnect(room_id, user_id)

# Create a global connection manager instance
manager = ConnectionManager() 