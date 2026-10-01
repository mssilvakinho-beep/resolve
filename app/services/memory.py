from app.core.db import connect

def memory(user_id: str):
    with connect() as conn:
        contacts=[dict(r) for r in conn.execute('SELECT * FROM contacts WHERE user_id=? ORDER BY created_at DESC',(user_id,)).fetchall()]
        cases=[dict(r) for r in conn.execute('SELECT * FROM cases WHERE user_id=? ORDER BY updated_at DESC',(user_id,)).fetchall()]
        events=[dict(r) for r in conn.execute('SELECT * FROM events WHERE user_id=? ORDER BY occurred_at DESC LIMIT 50',(user_id,)).fetchall()]
        transactions=[dict(r) for r in conn.execute('SELECT * FROM transactions WHERE user_id=? ORDER BY created_at DESC LIMIT 100',(user_id,)).fetchall()]
        documents=[dict(r) for r in conn.execute('SELECT * FROM documents WHERE user_id=? ORDER BY created_at DESC LIMIT 50',(user_id,)).fetchall()]
    return {'contacts':contacts,'cases':cases,'events':events,'transactions':transactions,'documents':documents}

def case_memory(case_id: str):
    with connect() as conn:
        case=conn.execute('SELECT * FROM cases WHERE id=?',(case_id,)).fetchone()
        if not case: return None
        events=[dict(r) for r in conn.execute('SELECT * FROM events WHERE case_id=? ORDER BY occurred_at DESC',(case_id,)).fetchall()]
        transactions=[dict(r) for r in conn.execute('SELECT * FROM transactions WHERE case_id=? ORDER BY created_at DESC',(case_id,)).fetchall()]
        documents=[dict(r) for r in conn.execute('SELECT * FROM documents WHERE case_id=? ORDER BY created_at DESC',(case_id,)).fetchall()]
    d=dict(case)
    d['events']=events; d['transactions']=transactions; d['documents']=documents
    d['receitas']=round(sum(x['amount'] for x in transactions if x['kind']=='RECEITA'),2)
    d['despesas']=round(sum(x['amount'] for x in transactions if x['kind']=='DESPESA'),2)
    d['saldo_registrado']=round(d['receitas']-d['despesas'],2)
    return d
