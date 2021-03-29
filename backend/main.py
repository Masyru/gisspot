from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from os import system

app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend/bundle/"), name="static")
templates = Jinja2Templates(directory="../frontend/")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    system("uvicorn main:app --reload")
