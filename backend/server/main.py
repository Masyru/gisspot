from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from os import system

from settings import STATIC_DIR, STATIC_URL
from router import router
# from backend.server.settings import STATIC_DIR, STATIC_URL
# from backend.server.router import router

app = FastAPI()

app.mount(STATIC_URL, StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router, tags=["core"])


if __name__ == '__main__':
    system("uvicorn main:app --reload")
