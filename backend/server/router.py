from fastapi import Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import sys
sys.path.append("../../")
from backend.server.core import manager
from backend.server.settings import TEMPLATES_DIR
from backend.server.ws import *
from backend.server.pd_model import *
from backend.queue.services import add_task

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    kwargs = {"url_pro_1": "C:\\Users\\Admin\\PycharmProjects\\gisspot\\backend\\database\\data\\pro\\NOAA_15_20210301_213305.f.pro",
              "url_pro_2": "C:\\Users\\Admin\\PycharmProjects\\gisspot\\backend\\database\\data\\pro\\NOAA_15_20210301_231345.f.pro",
              "points": ((30.0, 130.0),),
              "ws_id": "1",
              "deltatime": 6039,
              "window_size": (31, 31),
              "vicinity_size": (80, 80)}
    add_task(ws_id="1", kwargs=kwargs, task_type="high", args=())
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
    print(response)
    return response.json()
