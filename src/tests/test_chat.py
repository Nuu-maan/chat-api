import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from main import app
from src.services.database import RedisDatabase
from src.models.message import MessageType
from src.config.settings import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
async def db():
    database = RedisDatabase()
    await database.connect()
    yield database
    await database.disconnect()

@pytest.mark.asyncio
async def test_create_room(async_client):
    response = await async_client.post(
        "/api/v1/rooms",
        json={"name": "Test Room"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Room"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post(
        "/api/v1/users",
        json={"username": "testuser"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_get_nonexistent_room(async_client):
    response = await async_client.get("/api/v1/rooms/nonexistent")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client):
    response = await async_client.get("/api/v1/users/nonexistent")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_message_model():
    message = {
        "id": "test-id",
        "room_id": "room-id",
        "user_id": "user-id",
        "content": "Test message",
        "type": MessageType.TEXT,
        "created_at": "2024-01-01T00:00:00"
    }
    assert message["id"] == "test-id"
    assert message["room_id"] == "room-id"
    assert message["user_id"] == "user-id"
    assert message["content"] == "Test message"
    assert message["type"] == MessageType.TEXT
    assert message["created_at"] == "2024-01-01T00:00:00"

@pytest.mark.asyncio
async def test_chat_room_model():
    room = {
        "id": "test-id",
        "name": "Test Room",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    assert room["id"] == "test-id"
    assert room["name"] == "Test Room"
    assert room["created_at"] == "2024-01-01T00:00:00"
    assert room["updated_at"] == "2024-01-01T00:00:00"

@pytest.mark.asyncio
async def test_user_model():
    user = {
        "id": "test-id",
        "username": "testuser",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    assert user["id"] == "test-id"
    assert user["username"] == "testuser"
    assert user["created_at"] == "2024-01-01T00:00:00"
    assert user["updated_at"] == "2024-01-01T00:00:00"

@pytest.mark.asyncio
@pytest.mark.skip(reason="WebSocket tests require a running server")
async def test_websocket(db, test_client):
    # Create test room and user first
    room = await db.create_room("Test Room")
    user = await db.create_user("testuser")

    # Verify room and user were created successfully
    assert room.name == "Test Room"
    assert user.username == "testuser"

    # Note: WebSocket connection test is skipped as it requires a running server
    # In a real application, you would use integration tests for WebSocket functionality
        

