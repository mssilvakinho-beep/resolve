from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.services.audit import audit

def create_case(data):
    cid, now = new_id('case'), now_iso()
    with connect() as conn:
        conn.execute("INSERT INTO cases(id,user_id,contact_id,title,status,description,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                     (cid,data.user_id,data.contact_id,data.title,data.status,data.description,now,now)); conn.commit()
    audit(data.user_id,'CREATE','CASE',cid,{'title':data.title})
    return get_case(cid)

def get_case(cid):
    with connect() as conn:
        row=conn.execute("SELECT * FROM cases WHERE id=?",(cid,)).fetchone()
    return dict(row) if row else None

def list_cases(user_id, status=None):
    q="SELECT * FROM cases WHERE user_id=?"; args=[user_id]
    if status: q += " AND status=?"; args.append(status)
    q += " ORDER BY updated_at DESC"
    with connect() as conn: rows=conn.execute(q,args).fetchall()
    return [dict(r) for r in rows]

def update_status(cid,status):
    now=now_iso()
    with connect() as conn:
        row=conn.execute("SELECT user_id FROM cases WHERE id=?",(cid,)).fetchone()
        if not row: return None
        conn.execute("UPDATE cases SET status=?,updated_at=? WHERE id=?",(status,now,cid)); conn.commit()
    audit(row['user_id'],'UPDATE_STATUS','CASE',cid,{'status':status})
    return get_case(cid)
