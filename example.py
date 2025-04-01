import asyncio
import websockets
import json
import uuid
from datetime import datetime
import signal
import sys

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\nShutting down gracefully...")
    running = False

async def chat_client(user_id: str, chat_id: str):
    """Simulate a chat client"""
    uri = f"ws://localhost:8000/ws/{user_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected as {user_id}")
            
            # Join chat room
            join_message = {
                "type": "join",
                "chat_id": chat_id
            }
            await websocket.send(json.dumps(join_message))
            
            # Send typing indicator
            typing_message = {
                "type": "typing",
                "chat_id": chat_id,
                "is_typing": True
            }
            await websocket.send(json.dumps(typing_message))
            
            # Send actual message
            chat_message = {
                "type": "text",
                "chat_id": chat_id,
                "content": f"Hello from {user_id}!"
            }
            await websocket.send(json.dumps(chat_message))
            
            # Keep connection alive and receive messages
            while running:
                try:
                    message = await websocket.recv()
                    print(f"{user_id} received: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print(f"{user_id}: Connection closed while receiving messages")
                    break
                except Exception as e:
                    print(f"{user_id}: Error receiving message: {str(e)}")
                    break
            
            # Send leave message before closing
            try:
                leave_message = {
                    "type": "leave",
                    "chat_id": chat_id
                }
                await websocket.send(json.dumps(leave_message))
            except websockets.exceptions.ConnectionClosed:
                print(f"{user_id}: Connection closed before sending leave message")
            except Exception as e:
                print(f"{user_id}: Error sending leave message: {str(e)}")
                
    except Exception as e:
        print(f"{user_id}: Connection error: {str(e)}")

async def main():
    """Main function to run the chat simulation"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting chat simulation...")
    print("This will create 4 users in 2 different chat rooms")
    print("Press Ctrl+C to stop")
    
    # Create tasks for each client
    tasks = [
        chat_client("user1", "room1"),
        chat_client("user2", "room1"),
        chat_client("user3", "room2"),
        chat_client("user4", "room2")
    ]
    
    try:
        # Run all clients concurrently
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("\nSimulation cancelled by user")
    except Exception as e:
        print(f"\nSimulation error: {str(e)}")
    finally:
        print("Simulation ended")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation terminated by user")
    except Exception as e:
        print(f"\nSimulation failed: {str(e)}")
        sys.exit(1) 