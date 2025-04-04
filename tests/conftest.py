import pytest
import asyncio
from typing import AsyncGenerator, Generator
from src.services.database.redis import RedisDatabase
from src.config.settings import get_settings
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.main import app

settings = get_settings()

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db() -> AsyncGenerator[RedisDatabase, None]:
    """Create a Redis database instance for testing."""
    db = RedisDatabase()
    await db.connect()
    yield db
    await db.disconnect()

@pytest.fixture(autouse=True)
async def setup_database(db: RedisDatabase):
    """Clear the database before and after each test."""
    if db.redis_client:
        await db.redis_client.flushdb()
    yield
    if db.redis_client:
        await db.redis_client.flushdb()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an AsyncClient instance for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client