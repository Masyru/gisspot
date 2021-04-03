from fastapi import WebSocket
from typing import Dict, Optional, Union
from uuid import uuid4


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: Optional[WebSocket]) \
            -> Optional[str]:
        await websocket.accept()
        ws_id = str(uuid4())
        self.active_connections[ws_id] = websocket
        return ws_id

    def disconnect(self, websocket: Union[WebSocket, str]):
        if type(websocket) is str:
            del self.active_connections[websocket]
            return

        for key, item in self.active_connections.items():
            if item == websocket:
                del self.active_connections[key]
                return

    async def send_data(self, websocket: Union[str, WebSocket],
                        response_dict: Optional[dict]):
        if type(websocket) is str:
            websocket = self.active_connections[websocket]

        await websocket.send_json(response_dict)

    async def get_ws(self, ws_id: Optional[str]):
        return self.active_connections[ws_id]
