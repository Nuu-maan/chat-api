import pytest
from httpx import AsyncClient
from src.main import app
from src.services.database import RedisDatabase

@pytest.mark.asyncio
async def test_create_chat_room(db: RedisDatabase, async_client: AsyncClient):
    response = await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Room"

@pytest.mark.asyncio
async def test_get_chat_rooms(db: RedisDatabase, async_client: AsyncClient):
    # Create a room first
    await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    
    response = await async_client.get("/api/v1/rooms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

@pytest.mark.asyncio
async def test_create_user(db: RedisDatabase, async_client: AsyncClient):
    response = await async_client.post("/api/v1/users", json={"username": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_users(db: RedisDatabase, async_client: AsyncClient):
    # Create a user first
    await async_client.post("/api/v1/users", json={"username": "testuser"})
    
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

@pytest.mark.asyncio
async def test_send_message(db: RedisDatabase, async_client: AsyncClient):
    # Create a room and user first
    room_response = await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    user_response = await async_client.post("/api/v1/users", json={"username": "testuser"})
    user_id = user_response.json()["id"]
    
    # Send a message
    response = await async_client.post(
        f"/api/v1/rooms/{room_id}/messages",
        json={
            "content": "Hello, World!",
            "user_id": user_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello, World!"
    assert data["user_id"] == user_id
    assert data["room_id"] == room_id

@pytest.mark.asyncio
async def test_get_messages(db: RedisDatabase, async_client: AsyncClient):
    # Create a room and user first
    room_response = await async_client.post("/api/v1/rooms", json={"name": "Test Room"})
    room_id = room_response.json()["id"]
    
    user_response = await async_client.post("/api/v1/users", json={"username": "testuser"})
    user_id = user_response.json()["id"]
    
    # Send a message
    await async_client.post(
        f"/api/v1/rooms/{room_id}/messages",
        json={
            "content": "Hello, World!",
            "user_id": user_id
        }
    )
    
    # Get messages
    response = await async_client.get(f"/api/v1/rooms/{room_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["content"] == "Hello, World!" 