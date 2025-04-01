# Real-time Chat API

A modern, scalable real-time chat API built with FastAPI, WebSocket, and Redis.

## Features

- Real-time messaging using WebSocket
- Message persistence with Redis
- Support for multiple chat rooms
- Typing indicators
- Message history with pagination
- User presence tracking
- System messages for events
- Beautiful API documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **WebSocket**: Real-time bidirectional communication
- **Redis**: In-memory data store for message persistence
- **Pydantic**: Data validation using Python type annotations
- **Python 3.8+**: Modern Python features and type hints

## Prerequisites

- Python 3.8 or higher
- Redis server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nuu-maan/chat-api.git
cd chat-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
MAX_MESSAGES_PER_ROOM=1000
```

## Running the Application

1. Start Redis server:
```bash
redis-server
```

2. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc

## API Documentation

### WebSocket Endpoints

#### Connect to Chat
```websocket
ws://localhost:8000/ws/{user_id}
```

### HTTP Endpoints

#### Get Chat History
```http
GET /chat/{chat_id}/history
```

#### Get Chat Room Details
```http
GET /chat/{chat_id}
```

#### Get User Details
```http
GET /user/{user_id}
```

For detailed API documentation, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Example Usage

### Python Client
```python
import asyncio
import websockets
import json

async def chat_client():
    uri = "ws://localhost:8000/ws/user1"
    async with websockets.connect(uri) as websocket:
        # Join a chat room
        await websocket.send(json.dumps({
            "type": "join",
            "chat_id": "chat1"
        }))
        
        # Send a message
        await websocket.send(json.dumps({
            "type": "text",
            "content": "Hello, world!",
            "chat_id": "chat1"
        }))
        
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
    // Join a chat room
    ws.send(JSON.stringify({
        type: 'join',
        chat_id: 'chat1'
    }));
    
    // Send a message
    ws.send(JSON.stringify({
        type: 'text',
        content: 'Hello, world!',
        chat_id: 'chat1'
    }));
};
```

## Project Structure

```
chat-api/
├── config/
│   ├── __init__.py
│   └── settings.py
├── models/
│   ├── __init__.py
│   └── models.py
├── services/
│   ├── __init__.py
│   ├── database.py
│   └── websocket.py
├── static/
│   └── docs.html
├── main.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI team for the amazing framework
- Redis team for the powerful in-memory database
- All contributors who help improve this project 