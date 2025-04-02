import asyncio
import websockets
import json
import aiohttp
from typing import Dict, Any, Callable, Optional
from datetime import datetime

class ChatClient:
    def __init__(self, room_id: str, user_id: str, base_url: str = "http://localhost:8000"):
        self.room_id = room_id
        self.user_id = user_id
        self.base_url = base_url
        self.ws = None
        self.message_handlers: Dict[str, Callable] = {}
        self.connected = False

    async def connect(self):
        """Connect to the WebSocket server"""
        ws_url = f"ws://localhost:8000/ws/{self.room_id}/{self.user_id}"
        self.ws = await websockets.connect(ws_url)
        self.connected = True
        print("Connected to chat server")

        # Start message handler
        asyncio.create_task(self._handle_messages())

    async def disconnect(self):
        """Disconnect from the WebSocket server"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.connected = False
            print("Disconnected from chat server")

    async def send_message(self, content: str, metadata: Dict[str, Any] = None, reply_to: Optional[str] = None):
        """Send a message to the chat room"""
        if not self.connected:
            raise ConnectionError("Not connected to chat server")

        message = {
            "content": content,
            "metadata": metadata or {},
            "reply_to": reply_to
        }

        await self.ws.send(json.dumps(message))

    def on_message(self, handler: Callable):
        """Register a handler for new messages"""
        self.message_handlers["message"] = handler

    def on_history(self, handler: Callable):
        """Register a handler for chat history"""
        self.message_handlers["history"] = handler

    def on_system(self, handler: Callable):
        """Register a handler for system messages"""
        self.message_handlers["system"] = handler

    def on_error(self, handler: Callable):
        """Register a handler for error messages"""
        self.message_handlers["error"] = handler

    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                handler = self.message_handlers.get(data["type"])
                if handler:
                    await handler(data)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            self.connected = False
        except Exception as e:
            print(f"Error handling message: {e}")
            self.connected = False

    async def get_chat_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get chat history from the API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v1/rooms/{self.room_id}/messages",
                params={"limit": limit}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch chat history: {response.status}")
                return await response.json()

    async def get_room_details(self) -> Dict[str, Any]:
        """Get room details from the API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/v1/rooms/{self.room_id}") as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch room details: {response.status}")
                return await response.json()

    async def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user details from the API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/v1/users/{user_id}") as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch user details: {response.status}")
                return await response.json()

async def main():
    # Create chat client
    chat = ChatClient("room123", "user456")

    # Set up message handlers
    async def handle_message(data):
        print("New message:", data["message"])

    async def handle_history(data):
        print("Chat history:", data["messages"])

    async def handle_system(data):
        print("System message:", data["message"])

    async def handle_error(data):
        print("Error:", data["message"])

    chat.on_message(handle_message)
    chat.on_history(handle_history)
    chat.on_system(handle_system)
    chat.on_error(handle_error)

    # Connect to chat
    await chat.connect()

    # Send a message
    await chat.send_message("Hello, world!", {"type": "text"})

    # Get chat history
    history = await chat.get_chat_history()
    print("Chat history:", history)

    # Get room details
    room = await chat.get_room_details()
    print("Room details:", room)

    # Get user details
    user = await chat.get_user_details("user456")
    print("User details:", user)

    # Keep the connection alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await chat.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 