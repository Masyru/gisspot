from pathlib import Path

# DIRS
# Re-path base dir from backend to gisspot
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend"
STATIC_DIR = TEMPLATES_DIR / "bundle"
STATIC_URL = "/static/"
