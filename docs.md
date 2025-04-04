# Chat API Documentation

## Overview

The Chat API provides real-time messaging capabilities using WebSocket connections and Redis for data persistence. This document outlines the available endpoints and their usage.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses simple user IDs for authentication. Future versions will implement proper authentication mechanisms.

## Endpoints

### Chat Rooms

#### Create Room
```http
POST /rooms
```

Request body:
```json
{
    "name": "General Chat"
}
```

Response:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "General Chat",
    "created_at": "2024-01-01T12:00:00"
}
```

#### Get Rooms
```http
GET /rooms
```

Response:
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "General Chat",
        "created_at": "2024-01-01T12:00:00"
    }
]
```

### Users

#### Create User
```http
POST /users
```

Request body:
```json
{
    "username": "john_doe"
}
```

Response:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "john_doe",
    "created_at": "2024-01-01T12:00:00"
}
```

#### Get Users
```http
GET /users
```

Response:
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "john_doe",
        "created_at": "2024-01-01T12:00:00"
    }
]
```

### Messages

#### Send Message
```http
POST /rooms/{room_id}/messages
```

Request body:
```json
{
    "content": "Hello, world!",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "type": "text"
}
```

Response:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "content": "Hello, world!",
    "type": "text",
    "created_at": "2024-01-01T12:00:00"
}
```

#### Get Room Messages
```http
GET /rooms/{room_id}/messages
```

Query parameters:
- `limit` (optional): Maximum number of messages to return (default: 50)

Response:
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "room_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "content": "Hello, world!",
        "type": "text",
        "created_at": "2024-01-01T12:00:00"
    }
]
```

### WebSocket

#### Connect to Room
```
ws://localhost:8000/api/v1/ws/{room_id}/{user_id}
```

Upon connection, the server sends a history message with recent chat messages:
```json
{
    "type": "history",
    "messages": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "room_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "content": "Hello, world!",
            "type": "text",
            "created_at": "2024-01-01T12:00:00"
        }
    ]
}
```

#### Send WebSocket Message
```json
{
    "type": "text",
    "content": "Hello, everyone!"
}
```

#### Receive WebSocket Message
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "content": "Hello, everyone!",
    "type": "text",
    "created_at": "2024-01-01T12:00:00"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- HTTP endpoints: 60 requests per minute per IP
- WebSocket connections: 1 connection per user per room

## Data Storage

Messages are stored in Redis with the following characteristics:
- Messages expire after 7 days (configurable)
- Each room has a maximum of 100 messages (configurable)
- Room and user data are stored as Redis hashes
- Messages are stored as Redis lists with automatic trimming

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

WebSocket errors are handled with close codes:
- 4004: Room or User Not Found
- 1011: Internal Server Error 