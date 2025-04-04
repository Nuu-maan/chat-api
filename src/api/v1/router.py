from fastapi import APIRouter, WebSocket, HTTPException, Depends, Path
from typing import List
from pydantic import BaseModel
from src.models.chat_room import ChatRoom
from src.models.user import User
from src.models.message import Message, MessageType
from src.services.database import DatabaseInterface
from src.services.websocket import manager
from src.middleware.rate_limiter import check_rate_limit
from src.dependencies import get_database
import logging
import uuid
from datetime import datetime
from fastapi import WebSocketDisconnect

logger = logging.getLogger(__name__)
api_router = APIRouter()

class RoomCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str

class MessageCreate(BaseModel):
    content: str
    user_id: str
    type: MessageType = MessageType.TEXT

@api_router.post("/rooms", response_model=ChatRoom)
async def create_room(
    room: RoomCreate,
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Create a new chat room."""
    try:
        return await db.create_room(room.name)
    except Exception as e:
        logging.error(f"Error creating room: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/rooms", response_model=List[ChatRoom])
async def get_rooms(
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Get all chat rooms."""
    try:
        return await db.get_rooms()
    except Exception as e:
        logging.error(f"Error getting rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/rooms/{room_id}", response_model=ChatRoom)
async def get_room(
    room_id: str = Path(..., description="The ID of the room to retrieve"),
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Get a chat room by ID."""
    try:
        room = await db.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting room: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/users", response_model=User)
async def create_user(
    user: UserCreate,
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Create a new user."""
    try:
        return await db.create_user(user.username)
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users", response_model=List[User])
async def get_users(
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Get all users."""
    try:
        return await db.get_users()
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str = Path(..., description="The ID of the user to retrieve"),
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Get a user by ID."""
    try:
        user = await db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/rooms/{room_id}/messages", response_model=Message)
async def create_message(
    room_id: str,
    message: MessageCreate,
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Create a new message in a room."""
    try:
        # Verify room and user exist
        room = await db.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        user = await db.get_user(message.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create message
        msg = Message(
            id=str(uuid.uuid4()),
            room_id=room_id,
            user_id=message.user_id,
            content=message.content,
            type=message.type,
            created_at=datetime.utcnow()
        )

        await db.save_message(msg)
        return msg
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/rooms/{room_id}/messages", response_model=List[Message])
async def get_messages(
    room_id: str,
    limit: int = 50,
    db: DatabaseInterface = Depends(get_database),
    _: None = Depends(check_rate_limit)
):
    """Get messages from a room."""
    try:
        # Verify room exists
        room = await db.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        return await db.get_room_messages(room_id, limit)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str = Path(..., description="The ID of the room to connect to"),
    user_id: str = Path(..., description="The ID of the user connecting"),
    db: DatabaseInterface = Depends(get_database)
):
    """WebSocket endpoint for chat."""
    try:
        # Verify room and user exist
        room = await db.get_room(room_id)
        if not room:
            await websocket.close(code=4004, reason="Room not found")
            return

        user = await db.get_user(user_id)
        if not user:
            await websocket.close(code=4004, reason="User not found")
            return

        # Connect to WebSocket
        await manager.connect(websocket, room_id, user_id)
        
        try:
            # Send chat history
            messages = await db.get_room_messages(room_id)
            await websocket.send_json({
                "type": "history",
                "messages": [msg.dict() for msg in messages]
            })

            # Handle messages
            while True:
                data = await websocket.receive_json()
                if not isinstance(data, dict) or "type" not in data or "content" not in data:
                    continue

                message = Message(
                    id=str(uuid.uuid4()),
                    room_id=room_id,
                    user_id=user_id,
                    content=data["content"],
                    type=MessageType(data["type"]),
                    created_at=datetime.utcnow()
                )

                # Save message and broadcast to room
                await db.save_message(message)
                await manager.broadcast_to_room(room_id, message.dict())

        except WebSocketDisconnect:
            await manager.disconnect(websocket, room_id, user_id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await manager.disconnect(websocket, room_id, user_id)
            await websocket.close(code=1011, reason="Internal server error")
    except Exception as e:
        logger.error(f"WebSocket setup error: {e}")
        await websocket.close(code=1011, reason="Internal server error")

__all__ = ['api_router'] 