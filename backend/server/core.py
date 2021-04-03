from fastapi import FastAPI

from ws import ConnectionManager

app = FastAPI()
manager = ConnectionManager()
