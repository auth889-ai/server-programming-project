# core/realtime.py
from fastapi import Request, WebSocket
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List

class GlobalWorkoutNotifier:
    def __init__(self):
        self.listeners: set[asyncio.Queue] = set()

    async def subscribe(self):
        """Creates a new queue for a new visitor."""
        queue = asyncio.Queue()
        self.listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Removes the queue when the visitor leaves."""
        self.listeners.remove(queue)

    async def notify_new_workout(self, athlete_name: str, distance: float):
        """Broadcasts a workout notification to every active listener."""
        message = f"Athlete {athlete_name} just ran {distance}km!"
        payload = {
            "type": "workout",
            "message": message,
            "athlete": athlete_name,
            "distance": distance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Format for SSE (Server-Sent Events)
        sse_message = f"data: {json.dumps(payload)}\n\n"
        
        for queue in self.listeners:
            await queue.put(sse_message)


# Create a global instance
notifier = GlobalWorkoutNotifier()

async def event_generator(request: Request, queue: asyncio.Queue):
    """
    Generator function that yields SSE messages.
    """
    try:
        while True:
            # Check if the client has disconnected
            if await request.is_disconnected():
                print("Client disconnected from SSE stream")
                break
            
            try:
                # Wait for a message from the notifier
                # Timeout after 30 seconds to check for disconnection
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield message
                
                # Mark task as done
                queue.task_done()
                
            except asyncio.TimeoutError:
                # Send a heartbeat/keep-alive comment
                yield ": heartbeat\n\n"
                continue
                
    except asyncio.CancelledError:
        print("SSE generator cancelled")
    finally:
        # Always unsubscribe when done
        print("Unsubscribing from SSE notifications")
        notifier.unsubscribe(queue)


# ConnectionManager for WebSockets (for Task 3-4, keep it here)
class ConnectionManager:
    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

# Create a global instance for WebSocket management
manager = ConnectionManager()