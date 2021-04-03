from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from os import system

import sys
sys.path.append("../../")
from backend.server.core import app
from backend.server.settings import STATIC_DIR, STATIC_URL
from backend.server.router import router

app.mount(STATIC_URL, StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router, tags=["core"])


if __name__ == '__main__':
    system("uvicorn main:app --reload")
