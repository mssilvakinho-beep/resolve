from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.services.audit import audit

def create_contact(data):
    cid, now = new_id('ctc'), now_iso()
    with connect() as conn:
        conn.execute('INSERT INTO contacts(id,user_id,name,kind,created_at) VALUES(?,?,?,?,?)',(cid,data.user_id,data.name,data.kind,now)); conn.commit()
    audit(data.user_id,'CREATE','CONTACT',cid,data.model_dump())
    return {'id':cid,'user_id':data.user_id,'name':data.name,'kind':data.kind,'created_at':now}

def list_contacts(user_id):
    with connect() as conn: rows=conn.execute('SELECT * FROM contacts WHERE user_id=? ORDER BY created_at DESC',(user_id,)).fetchall()
    return [dict(r) for r in rows]
