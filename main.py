from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import json
from datetime import datetime
import uuid
from models import Message, ChatRoom, User, ChatResponse, TypingStatus, MessageType
from services.websocket import manager
from services.database import db
from config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            message_type = message_data.get("type", "message")
            
            if message_type == "join":
                chat_id = message_data.get("chat_id")
                if chat_id:
                    await manager.join_chat(user_id, chat_id)
            
            elif message_type == "leave":
                chat_id = message_data.get("chat_id")
                if chat_id:
                    await manager.leave_chat(user_id, chat_id)
            
            elif message_type == "typing":
                chat_id = message_data.get("chat_id")
                is_typing = message_data.get("is_typing", False)
                if chat_id:
                    await manager.handle_typing(user_id, chat_id, is_typing)
            
            else:  # Regular message
                chat_id = message_data.get("chat_id")
                content = message_data.get("content", "")
                reply_to = message_data.get("reply_to")
                
                if chat_id and content:
                    message = Message(
                        id=str(uuid.uuid4()),
                        chat_id=chat_id,
                        user_id=user_id,
                        content=content,
                        type=MessageType.TEXT,
                        timestamp=datetime.utcnow(),
                        reply_to=reply_to
                    )
                    
                    # Save message to database
                    await db.save_message(message)
                    
                    # Broadcast to chat room
                    await manager.broadcast_to_chat(chat_id, message)
            
    except WebSocketDisconnect:
        await manager.disconnect(user_id)

@app.get("/chat/{chat_id}/history")
async def get_chat_history(
    chat_id: str,
    limit: int = 50,
    before: Optional[datetime] = None
) -> ChatResponse:
    """Get chat history with pagination"""
    messages = await db.get_messages(chat_id, limit, before)
    return ChatResponse(
        messages=messages,
        has_more=len(messages) == limit,
        next_cursor=messages[-1].id if messages else None
    )

@app.get("/chat/{chat_id}")
async def get_chat_room(chat_id: str) -> ChatRoom:
    """Get chat room details"""
    chat_room = await db.get_chat_room(chat_id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return chat_room

@app.get("/user/{user_id}")
async def get_user(user_id: str) -> User:
    """Get user details"""
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_class=HTMLResponse)
async def get_docs():
    """Serve the API documentation page"""
    with open("static/docs.html", "r", encoding="utf-8") as f:
        return f.read()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 