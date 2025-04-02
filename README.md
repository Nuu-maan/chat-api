# Chat API

A real-time chat API built with FastAPI, WebSockets, and Redis.

## Features

- Real-time messaging using WebSockets
- Chat rooms with multiple users
- Message history
- User management
- Rate limiting
- Asynchronous operations
- Redis for data persistence
- Comprehensive test suite

## Project Structure

```
chat-api/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   │   └── v1/           # API v1 routes
│   ├── config/           # Configuration settings
│   ├── core/             # Core business logic
│   ├── examples/         # Example usage
│   ├── middleware/       # Middleware components
│   ├── models/          # Data models
│   └── services/        # Services (Database, WebSocket)
├── tests/               # Test suite
├── static/             # Static files
├── .env               # Environment variables
├── example.env        # Example environment variables
├── requirements.txt   # Python dependencies
├── setup.py          # Package setup
├── pytest.ini        # Pytest configuration
└── README.md         # Project documentation
```

## Prerequisites

- Python 3.8+
- Redis server
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat-api.git
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

4. Copy example.env to .env and configure your settings:
```bash
cp example.env .env
```

## Configuration

Edit `.env` file to configure:

- Redis connection settings
- API settings
- Rate limiting parameters
- Logging configuration

## Running the API

1. Start the Redis server

2. Run the FastAPI server:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## WebSocket Endpoints

### Connect to Chat Room
```
ws://localhost:8000/api/v1/ws/{room_id}/{user_id}
```

### Message Format
```json
{
    "type": "text",
    "content": "Hello, World!",
    "user_id": "user123"
}
```

## REST Endpoints

### Rooms
- `POST /api/v1/rooms` - Create room
- `GET /api/v1/rooms` - List rooms
- `GET /api/v1/rooms/{room_id}` - Get room
- `GET /api/v1/rooms/{room_id}/messages` - Get room messages

### Users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{user_id}` - Get user

### Messages
- `POST /api/v1/rooms/{room_id}/messages` - Send message

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 