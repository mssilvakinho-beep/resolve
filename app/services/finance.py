from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.services.audit import audit

def create_transaction(data):
    tid=new_id('txn')
    with connect() as conn:
        conn.execute("INSERT INTO transactions(id,user_id,case_id,contact_id,kind,category,description,amount,due_date,paid,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                     (tid,data.user_id,data.case_id,data.contact_id,data.kind,data.category,data.description,data.amount,data.due_date,int(data.paid),now_iso())); conn.commit()
    audit(data.user_id,'CREATE','TRANSACTION',tid,data.model_dump())
    return get_transaction(tid)

def get_transaction(tid):
    with connect() as conn: row=conn.execute("SELECT * FROM transactions WHERE id=?",(tid,)).fetchone()
    return dict(row) if row else None

def list_transactions(user_id, kind=None):
    q="SELECT * FROM transactions WHERE user_id=?"; args=[user_id]
    if kind: q += " AND kind=?"; args.append(kind)
    q += " ORDER BY created_at DESC"
    with connect() as conn: rows=conn.execute(q,args).fetchall()
    return [dict(r) for r in rows]

def summary(user_id):
    with connect() as conn:
        r=conn.execute("SELECT COALESCE(SUM(CASE WHEN kind='RECEITA' THEN amount ELSE 0 END),0) receitas, COALESCE(SUM(CASE WHEN kind='DESPESA' THEN amount ELSE 0 END),0) despesas, COALESCE(SUM(CASE WHEN kind='RECEITA' AND paid=0 THEN amount ELSE 0 END),0) a_receber, COALESCE(SUM(CASE WHEN kind='DESPESA' AND paid=0 THEN amount ELSE 0 END),0) a_pagar FROM transactions WHERE user_id=?",(user_id,)).fetchone()
    d=dict(r); d['saldo_registrado']=round(d['receitas']-d['despesas'],2); return d
