from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from os import system

from .settings import STATIC_DIR, STATIC_URL
import router

app = FastAPI()

app.mount(STATIC_URL, StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router.router_core, tags=["core"])


if __name__ == '__main__':
    system("uvicorn main:app --reload")
