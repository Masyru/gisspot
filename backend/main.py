from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from os import system

from .settings import TEMPLATES_DIR, STATIC_DIR, STATIC_URL
from .ws import ConnectionManager, processing_ws

app = FastAPI()
manager = ConnectionManager()

app.mount(STATIC_URL, StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/")
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


if __name__ == '__main__':
    system("uvicorn main:app --reload")
