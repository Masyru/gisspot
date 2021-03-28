from fastapi import WebSocket
from typing import List, Optional


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: Optional[WebSocket]):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: Optional[WebSocket]):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_data(response_dict: Optional[dict],
                        websocket: Optional[WebSocket]):
        await websocket.send_json(response_dict)
