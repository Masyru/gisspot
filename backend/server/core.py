from fastapi import FastAPI

import sys
sys.path.append("../../")
from backend.server.ws import ConnectionManager

app = FastAPI()
manager = ConnectionManager()
