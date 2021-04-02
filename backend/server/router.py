from fastapi import Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .services import *
from .settings import TEMPLATES_DIR
from .ws import *
from .pd_model import *

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)
manager = ConnectionManager()


@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    ws_id: str = await manager.connect(websocket)
    try:
        while True:
            data: dict = await websocket.receive_json()
            user_request(ws_id, StandardModel(**data))

    except WebSocketDisconnect:
        manager.disconnect(ws_id)


@router.post("/processing/", response_class=JSONResponse)
async def processing_endpoint(data: StandardModel):
    response: StandardModel = service_request(data)
    return response.json()
