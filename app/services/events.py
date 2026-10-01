from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.services.audit import audit

def create_event(data):
    eid=new_id('evt'); ts=now_iso()
    with connect() as conn:
        conn.execute("INSERT INTO events(id,user_id,case_id,contact_id,type,description,amount,occurred_at) VALUES(?,?,?,?,?,?,?,?)",
                     (eid,data.user_id,data.case_id,data.contact_id,data.type,data.description,data.amount,ts)); conn.commit()
    audit(data.user_id,'CREATE','EVENT',eid,data.model_dump())
    with connect() as conn: row=conn.execute("SELECT * FROM events WHERE id=?",(eid,)).fetchone()
    return dict(row)
