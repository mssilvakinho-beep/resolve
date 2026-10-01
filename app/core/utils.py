from datetime import datetime, timezone
import uuid

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
