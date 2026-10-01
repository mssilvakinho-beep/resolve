import os

APP_VERSION = "2.0.1-core-interpreter"

def db_path() -> str:
    return os.getenv("RESOLVE_DB", "data/resolve.db")
