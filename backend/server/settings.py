from pathlib import Path

# DIRS
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "build"
STATIC_DIR = BASE_DIR / "build/static"
STATIC_URL = "/static/"

DATABASE_URL = ""

# Request/Response types
REQUEST_TYPES = ("fetchPreview", "getVectors",
                 "connectVectors", "refuseVectors")
