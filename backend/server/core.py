from fastapi import FastAPI
from backend.server.ws import ConnectionManager

app = FastAPI()
manager = ConnectionManager()
