# Chat API

A real-time chat API built with FastAPI, WebSockets, and Redis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Nuu-maan/chat-api/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/redis-7.0+-red.svg)](https://redis.io)

## Features

- Real-time messaging using WebSockets
- Chat rooms with multiple users
- Message history and persistence
- User management and authentication
- Rate limiting and security features
- Asynchronous operations
- Redis for data storage
- Comprehensive test suite

## Project Structure

```
chat-api/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   │   └── v1/           # API v1 routes
│   ├── config/           # Configuration settings
│   ├── core/             # Core business logic
│   ├── middleware/       # Middleware components
│   ├── models/          # Data models
│   └── services/        # Services (Database, WebSocket)
├── tests/               # Test suite
├── static/             # Static files and documentation assets
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

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Nuu-maan/chat-api.git
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

Visit the beautiful documentation at:
- `/` - Main documentation with Swagger UI
- `/redoc` - Alternative documentation with ReDoc

## WebSocket Usage

### Connect to Chat Room
```
ws://localhost:8000/api/v1/ws/{room_id}/{user_id}
```

### Message Format
```json
{
    "type": "text",
    "content": "Hello, World!",
    "user_id": "user123",
    "room_id": "room456"
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

Contributions are greatly appreciated! Here's how you can help:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

### Areas for Contribution
* Additional features and endpoints
* Performance improvements
* Documentation enhancements
* Bug fixes
* Test coverage improvements
* Security enhancements

### Development Guidelines
* Follow PEP 8 style guide
* Write tests for new features
* Update documentation for changes
* Keep commits atomic and well-described
* Add type hints to new code

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Nuu-maan/chat-api/blob/main/LICENSE) file for details.

## Repository

Visit the project repository at [https://github.com/Nuu-maan/chat-api](https://github.com/Nuu-maan/chat-api) 