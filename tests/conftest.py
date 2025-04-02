import pytest
import asyncio
from typing import Generator
from src.services.database import RedisDatabase
from fastapi.testclient import TestClient
from src.main import app
from httpx import AsyncClient

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create a new event loop policy for the test session."""
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    return policy

@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """Create an instance of the default event loop for each test case."""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db():
    """Create a RedisDatabase instance for testing."""
    database = RedisDatabase()
    await database.connect()
    yield database
    await database.disconnect()

@pytest.fixture(autouse=True)
async def setup_database(db: RedisDatabase):
    """Clear the database before and after each test."""
    await db.redis_client.flushdb()
    yield
    await db.redis_client.flushdb()

@pytest.fixture
async def async_client():
    """Create an AsyncClient instance for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client 