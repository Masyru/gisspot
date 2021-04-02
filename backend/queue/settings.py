from pathlib import Path

# DIRS
BASE_DIR = Path(__file__).resolve().parent.parent
REDIS_URL = ""

# TIME
RESULT_TTL = 600
TTL = None
FAILURE_TTL = 600

SERVER_URL = "localhost:8800/service/"