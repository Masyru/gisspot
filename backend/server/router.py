from fastapi import Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.server.settings import TEMPLATES_DIR
from backend.server.ws import ConnectionManager, processing_user
from backend.server.pd_model import *

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)
manager = ConnectionManager()


@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data: dict = await websocket.receive_json()
            processing_user(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/processing/{ws_id}")
async def processing_endpoint(data: ProcessingData, ws_id: int):
    ws = await manager.get_ws(ws_id)
    await manager.send_data(response_dict={"type": "Point", "data": data},
                            websocket=ws)
