# Chat API Documentation

## Overview
This is a real-time chat API built with FastAPI and WebSocket support. The API allows users to connect to chat rooms, send messages, and receive real-time updates.

## Base URL
```
http://localhost:8000
```

## WebSocket Endpoints

### Connect to Chat Room
```websocket
ws://localhost:8000/ws/{user_id}
```

Connects a user to the chat system. The user will receive real-time updates for messages and system events.

#### Parameters
- `user_id` (path): Unique identifier for the user

#### Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user1');
```

## HTTP Endpoints

### Get Chat History
```http
GET /chat/{chat_id}/messages
```

Retrieves the message history for a specific chat room.

#### Parameters
- `chat_id` (path): Unique identifier for the chat room
- `limit` (query, optional): Maximum number of messages to return (default: 50)
- `before` (query, optional): Timestamp to get messages before (ISO format)

#### Response
```json
[
  {
    "id": "uuid",
    "chat_id": "uuid",
    "user_id": "uuid",
    "content": "Message content",
    "type": "text",
    "timestamp": "2024-01-01T00:00:00",
    "metadata": {},
    "reply_to": null
  }
]
```

### Get Chat Room Details
```http
GET /chat/{chat_id}
```

Retrieves details about a specific chat room.

#### Parameters
- `chat_id` (path): Unique identifier for the chat room

#### Response
```json
{
  "id": "uuid",
  "name": "Chat Room Name",
  "created_at": "2024-01-01T00:00:00",
  "participants": ["user1", "user2"],
  "is_private": false,
  "metadata": {}
}
```

### Get User Details
```http
GET /user/{user_id}
```

Retrieves details about a specific user.

#### Parameters
- `user_id` (path): Unique identifier for the user

#### Response
```json
{
  "id": "uuid",
  "username": "username",
  "email": "user@example.com",
  "is_active": true,
  "last_seen": "2024-01-01T00:00:00",
  "metadata": {}
}
```

## Message Types

### Text Message
```json
{
  "type": "text",
  "content": "Hello, world!",
  "chat_id": "uuid",
  "user_id": "uuid"
}
```

### System Message
```json
{
  "type": "system",
  "content": "User joined the chat",
  "chat_id": "uuid",
  "user_id": "system"
}
```

### Typing Status
```json
{
  "type": "typing",
  "content": "typing",
  "chat_id": "uuid",
  "user_id": "uuid"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting
- Maximum messages per chat room: 1000 (configurable in settings)
- WebSocket connection timeout: 5 seconds
- Redis connection timeout: 5 seconds

## Security
- CORS is enabled for all origins
- WebSocket connections are authenticated via user_id
- Redis connection uses password authentication

## Dependencies
- FastAPI
- Redis
- WebSockets
- Pydantic
- Python 3.8+

## Configuration
The application can be configured through environment variables or a `.env` file:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
MAX_MESSAGES_PER_ROOM=1000
```

## Example Usage

### Python Client
```python
import asyncio
import websockets
import json

async def chat_client():
    uri = "ws://localhost:8000/ws/user1"
    async with websockets.connect(uri) as websocket:
        # Send a text message
        message = {
            "type": "text",
            "content": "Hello, world!",
            "chat_id": "chat1",
            "user_id": "user1"
        }
        await websocket.send(json.dumps(message))
        
        # Receive messages
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(chat_client())
```

### JavaScript Client
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user1');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};

ws.onopen = () => {
    // Send a text message
    const message = {
        type: 'text',
        content: 'Hello, world!',
        chat_id: 'chat1',
        user_id: 'user1'
    };
    ws.send(JSON.stringify(message));
};
``` 