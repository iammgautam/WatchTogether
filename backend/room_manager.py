from fastapi import WebSocket
from typing import Dict, List, Any
import json

class ConnectionManager:
    def __init__(self):
        # Dict[room_id, Dict[user_id, WebSocket]]
        self.active_connections: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, room_id: str, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: str, user_id: int):
        if room_id in self.active_connections:
            if user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            # Create a list of tasks to send concurrently
            payload = json.dumps(message, default=str)
            for user_id, connection in self.active_connections[room_id].items():
                try:
                    await connection.send_text(payload)
                except Exception:
                    # Connection might be closed, handle in disconnect
                    pass

    async def send_to_user(self, room_id: str, user_id: int, message: dict):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            payload = json.dumps(message, default=str)
            try:
                await self.active_connections[room_id][user_id].send_text(payload)
            except Exception:
                pass

manager = ConnectionManager()
