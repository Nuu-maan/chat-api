from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.chat_room import ChatRoom
from src.models.user import User
from src.models.message import Message

class DatabaseInterface(ABC):
    """Abstract base class defining the database interface."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        pass
    
    @abstractmethod
    async def create_room(self, name: str) -> ChatRoom:
        """Create a new chat room."""
        pass
    
    @abstractmethod
    async def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID."""
        pass
    
    @abstractmethod
    async def get_rooms(self) -> List[ChatRoom]:
        """Get all chat rooms."""
        pass
    
    @abstractmethod
    async def create_user(self, username: str) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        pass
    
    @abstractmethod
    async def get_users(self) -> List[User]:
        """Get all users."""
        pass
    
    @abstractmethod
    async def save_message(self, message: Message) -> None:
        """Save a message."""
        pass
    
    @abstractmethod
    async def get_room_messages(self, room_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a room."""
        pass 