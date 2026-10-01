from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.services.audit import audit

def create_document(data):
    did, now = new_id('doc'), now_iso()
    with connect() as conn:
        conn.execute('INSERT INTO documents(id,user_id,case_id,contact_id,filename,document_type,storage_ref,created_at) VALUES(?,?,?,?,?,?,?,?)',
                     (did,data.user_id,data.case_id,data.contact_id,data.filename,data.document_type,data.storage_ref,now)); conn.commit()
    audit(data.user_id,'CREATE','DOCUMENT',did,data.model_dump())
    return get_document(did)

def get_document(did):
    with connect() as conn: row=conn.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
    return dict(row) if row else None

def list_documents(user_id, case_id=None):
    q='SELECT * FROM documents WHERE user_id=?'; args=[user_id]
    if case_id: q+=' AND case_id=?'; args.append(case_id)
    q+=' ORDER BY created_at DESC'
    with connect() as conn: rows=conn.execute(q,args).fetchall()
    return [dict(r) for r in rows]
