import asyncio
import websockets
import json
import uuid
from datetime import datetime
import logging
import httpx
from websockets.exceptions import ConnectionClosed
import sys
import signal

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    logger.info("Shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

async def create_room_and_user():
    """Create a test room and user"""
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Create a room
            room_name = f"test-room-{uuid.uuid4()}"
            logger.info(f"Creating room: {room_name}")
            room_response = await client.post(
                "http://localhost:8000/api/v1/rooms",
                params={"name": room_name}
            )
            room_response.raise_for_status()
            room_data = room_response.json()
            room_id = room_data["id"]
            logger.info(f"Created room: {room_data}")

            # Create a user
            username = f"test-user-{uuid.uuid4()}"
            logger.info(f"Creating user: {username}")
            user_response = await client.post(
                "http://localhost:8000/api/v1/users",
                params={"username": username}
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            user_id = user_data["id"]
            logger.info(f"Created user: {user_data}")

            return room_id, user_id
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating room/user: {e}")
            raise

async def chat_example():
    """Run the chat example"""
    try:
        # Create room and user
        room_id, user_id = await create_room_and_user()
        logger.info(f"Using room_id: {room_id}, user_id: {user_id}")
        
        # Connect to WebSocket
        uri = f"ws://localhost:8000/api/v1/ws/{room_id}/{user_id}"
        logger.info(f"Connecting to WebSocket at: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("Successfully connected to WebSocket")
            
            # Send a message
            message = {
                "type": "message",
                "content": "Hello, World!",
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Sending message: {message}")
            await websocket.send(json.dumps(message))
            logger.info("Message sent successfully")
            
            # Receive messages
            while running:
                try:
                    response = await websocket.recv()
                    logger.info(f"Received: {response}")
                except ConnectionClosed as e:
                    logger.error(f"Connection closed: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
                    
    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"Failed to connect: Invalid status code - {e}")
    except ConnectionClosed as e:
        logger.error(f"Connection closed unexpectedly: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

async def main():
    """Main entry point"""
    try:
        logger.info("Starting chat simulation...")
        logger.info("This will create a test room and user, then connect to the chat")
        logger.info("Press Ctrl+C to stop")
        await chat_example()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    finally:
        logger.info("Simulation ended")

if __name__ == "__main__":
    asyncio.run(main()) 