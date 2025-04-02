import pytest
import websockets
from httpx import AsyncClient
from src.main import app
from src.services.database import RedisDatabase
import json
import asyncio
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection(db: RedisDatabase, async_client: AsyncClient):
    # Create a room first
    room_response = await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Create a user
    user_response = await async_client.post("/api/v1/users", json={"username": "testuser"})
    user_id = user_response.json()["id"]
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/api/v1/ws/{room_id}/{user_id}"
    async with websockets.connect(uri) as websocket:
        # First receive the history message
        history = json.loads(await websocket.recv())
        assert history["type"] == "history"
        assert isinstance(history["messages"], list)
        
        # Send a message
        await websocket.send(json.dumps({
            "type": "text",
            "content": "Hello, World!",
            "user_id": user_id
        }))
        
        # Receive the message back
        data = json.loads(await websocket.recv())
        assert data["type"] == "text"
        assert data["content"] == "Hello, World!"
        assert data["user_id"] == user_id
        assert data["room_id"] == room_id

@pytest.mark.asyncio
async def test_websocket_broadcast(db: RedisDatabase, async_client: AsyncClient):
    # Create a room first
    room_response = await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    # Create two users
    user1_response = await async_client.post("/api/v1/users", json={"username": "user1"})
    user1_id = user1_response.json()["id"]
    
    user2_response = await async_client.post("/api/v1/users", json={"username": "user2"})
    user2_id = user2_response.json()["id"]
    
    # Connect two clients to the same room
    uri1 = f"ws://localhost:8000/api/v1/ws/{room_id}/{user1_id}"
    uri2 = f"ws://localhost:8000/api/v1/ws/{room_id}/{user2_id}"
    
    async with websockets.connect(uri1) as websocket1, \
              websockets.connect(uri2) as websocket2:
        
        # First receive the history messages
        history1 = json.loads(await websocket1.recv())
        history2 = json.loads(await websocket2.recv())
        assert history1["type"] == "history"
        assert history2["type"] == "history"
        
        # Send a message from the first client
        await websocket1.send(json.dumps({
            "type": "text",
            "content": "Hello from user1!",
            "user_id": user1_id
        }))
        
        # Both clients should receive the message
        data1 = json.loads(await websocket1.recv())
        data2 = json.loads(await websocket2.recv())
        
        assert data1["type"] == "text"
        assert data1["content"] == "Hello from user1!"
        assert data1["user_id"] == user1_id
        
        assert data2["type"] == "text"
        assert data2["content"] == "Hello from user1!"
        assert data2["user_id"] == user1_id 