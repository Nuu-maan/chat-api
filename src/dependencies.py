from functools import lru_cache
from src.services.database import DatabaseInterface, RedisDatabase

@lru_cache()
def get_database() -> DatabaseInterface:
    """Get database instance with dependency injection."""
    return RedisDatabase() 