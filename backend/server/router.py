from fastapi import Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.server.settings import TEMPLATES_DIR
from backend.server.ws import ConnectionManager, processing_ws

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
            response_data: dict = processing_ws(data)
            await manager.send_data(response_dict=response_data,
                                    websocket=websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
