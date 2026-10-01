import json
from app.core.db import connect
from app.core.utils import new_id, now_iso

def audit(user_id, action, entity_type, entity_id=None, detail=None):
    with connect() as conn:
        conn.execute(
            "INSERT INTO audit_log(id,user_id,action,entity_type,entity_id,detail,created_at) VALUES(?,?,?,?,?,?,?)",
            (new_id('aud'), user_id, action, entity_type, entity_id, json.dumps(detail or {}, ensure_ascii=False), now_iso())
        )
        conn.commit()
