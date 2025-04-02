# Chat API Documentation

## Overview

The Chat API provides real-time messaging capabilities using WebSockets and REST endpoints. It supports multiple chat rooms, user management, and message persistence using Redis.

## Authentication

Currently, the API uses simple user IDs for authentication. In a production environment, you should implement proper authentication using JWT or similar.

## WebSocket API

### Connect to Chat Room

```
ws://localhost:8000/api/v1/ws/{room_id}/{user_id}
```

#### Parameters
- `room_id`: The ID of the chat room to connect to
- `user_id`: The ID of the user connecting

#### Message Types

1. Text Message
```json
{
    "type": "text",
    "content": "Hello, World!",
    "user_id": "user123"
}
```

2. History Message (Server -> Client)
```json
{
    "type": "history",
    "messages": [
        {
            "id": "message123",
            "room_id": "room123",
            "user_id": "user123",
            "content": "Hello!",
            "type": "text",
            "created_at": "2024-04-01T12:00:00Z"
        }
    ]
}
```

3. System Message (Server -> Client)
```json
{
    "type": "system",
    "content": "User user123 left the chat",
    "timestamp": "2024-04-01T12:00:00Z"
}
```

## REST API

### Rooms

#### Create Room
```http
POST /api/v1/rooms
Content-Type: application/json

{
    "name": "General Chat"
}
```

Response:
```json
{
    "id": "room123",
    "name": "General Chat",
    "created_at": "2024-04-01T12:00:00Z"
}
```

#### List Rooms
```http
GET /api/v1/rooms
```

Response:
```json
[
    {
        "id": "room123",
        "name": "General Chat",
        "created_at": "2024-04-01T12:00:00Z"
    }
]
```

#### Get Room
```http
GET /api/v1/rooms/{room_id}
```

Response:
```json
{
    "id": "room123",
    "name": "General Chat",
    "created_at": "2024-04-01T12:00:00Z"
}
```

### Users

#### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
    "username": "john_doe"
}
```

Response:
```json
{
    "id": "user123",
    "username": "john_doe",
    "created_at": "2024-04-01T12:00:00Z"
}
```

#### List Users
```http
GET /api/v1/users
```

Response:
```json
[
    {
        "id": "user123",
        "username": "john_doe",
        "created_at": "2024-04-01T12:00:00Z"
    }
]
```

#### Get User
```http
GET /api/v1/users/{user_id}
```

Response:
```json
{
    "id": "user123",
    "username": "john_doe",
    "created_at": "2024-04-01T12:00:00Z"
}
```

### Messages

#### Send Message
```http
POST /api/v1/rooms/{room_id}/messages
Content-Type: application/json

{
    "content": "Hello, World!",
    "user_id": "user123",
    "type": "text"
}
```

Response:
```json
{
    "id": "message123",
    "room_id": "room123",
    "user_id": "user123",
    "content": "Hello, World!",
    "type": "text",
    "created_at": "2024-04-01T12:00:00Z"
}
```

#### Get Room Messages
```http
GET /api/v1/rooms/{room_id}/messages?limit=50
```

Response:
```json
[
    {
        "id": "message123",
        "room_id": "room123",
        "user_id": "user123",
        "content": "Hello, World!",
        "type": "text",
        "created_at": "2024-04-01T12:00:00Z"
    }
]
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

Error Response Format:
```json
{
    "detail": "Error message here"
}
```

## Rate Limiting

The API implements rate limiting per client IP address. The default limit is configurable in the `.env` file.

## WebSocket Events

1. Connection
   - Client connects to WebSocket
   - Server sends chat history
   - Server notifies other users of new connection

2. Message
   - Client sends message
   - Server broadcasts message to all users in room
   - Server persists message in Redis

3. Disconnection
   - Client disconnects
   - Server notifies other users
   - Server cleans up connection

## Examples

### Python Client Example
```python
import asyncio
import websockets
import json

async def chat_client():
    uri = "ws://localhost:8000/api/v1/ws/room123/user123"
    async with websockets.connect(uri) as websocket:
        # Receive history
        history = await websocket.recv()
        print(f"History: {history}")
        
        # Send message
        message = {
            "type": "text",
            "content": "Hello!",
            "user_id": "user123"
        }
        await websocket.send(json.dumps(message))
        
        # Receive messages
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(chat_client())
```

### JavaScript Client Example
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/room123/user123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'text',
        content: 'Hello!',
        user_id: 'user123'
    }));
};
``` 