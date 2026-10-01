import json
from app.core.db import connect
from app.core.utils import new_id, now_iso
from app.ai.interpreter import interpret_ptbr
from app.ai.openai_adapter import available, interpret_with_openai
from app.services.contacts import create_contact
from app.services.cases import create_case
from app.services.finance import create_transaction
from app.services.events import create_event
from app.models.schemas import ContactIn, CaseIn, TransactionIn, EventIn

def propose(user_id,text):
    source="local"
    if available():
        try:
            proposal=interpret_with_openai(text)
            source="openai"
        except Exception as e:
            proposal=interpret_ptbr(text)
            proposal["notes"]=(proposal.get("notes") or "") + " Fallback local por indisponibilidade temporária da IA."
    else:
        proposal=interpret_ptbr(text)
    iid=new_id('int')
    with connect() as conn:
        conn.execute('INSERT INTO interpretations(id,user_id,text,proposal_json,status,created_at) VALUES(?,?,?,?,?,?)',
            (iid,user_id,text,json.dumps(proposal,ensure_ascii=False),'PENDENTE',now_iso())); conn.commit()
    return {'interpretation_id':iid,'status':'PENDENTE','source':source,'proposal':proposal}

def confirm(interpretation_id):
    with connect() as conn:
        row=conn.execute('SELECT * FROM interpretations WHERE id=?',(interpretation_id,)).fetchone()
    if not row: return None
    if row['status']=='CONFIRMADA': return {'interpretation_id':interpretation_id,'status':'CONFIRMADA'}
    proposal=json.loads(row['proposal_json']); uid=row['user_id']; created=[]
    contact_id=None
    if proposal.get('contact_name'):
        # Reuse exact existing contact for this user when possible.
        with connect() as conn:
            c=conn.execute('SELECT id FROM contacts WHERE user_id=? AND lower(name)=lower(?) LIMIT 1',(uid,proposal['contact_name'])).fetchone()
        contact_id=c['id'] if c else create_contact(ContactIn(user_id=uid,name=proposal['contact_name'],kind='contato'))['id']
        created.append({'type':'CONTACT','id':contact_id}) if not c else None
    case_id=None
    if proposal.get('case_title'):
        case_id=create_case(CaseIn(user_id=uid,contact_id=contact_id,title=proposal['case_title']))['id']
        created.append({'type':'CASE','id':case_id})
    if proposal.get('revenue'):
        x=create_transaction(TransactionIn(user_id=uid,case_id=case_id,contact_id=contact_id,kind='RECEITA',category='RECEITA',description=row['text'],amount=proposal['revenue'],paid=True)); created.append({'type':'TRANSACTION','id':x['id']})
    if proposal.get('expense'):
        x=create_transaction(TransactionIn(user_id=uid,case_id=case_id,contact_id=contact_id,kind='DESPESA',category=proposal.get('expense_category') or 'OUTROS',description=row['text'],amount=proposal['expense'],paid=True)); created.append({'type':'TRANSACTION','id':x['id']})
    if not created:
        x=create_event(EventIn(user_id=uid,case_id=case_id,contact_id=contact_id,type='NOTA',description=row['text'])); created.append({'type':'EVENT','id':x['id']})
    with connect() as conn:
        conn.execute("UPDATE interpretations SET status='CONFIRMADA',confirmed_at=? WHERE id=?",(now_iso(),interpretation_id)); conn.commit()
    return {'interpretation_id':interpretation_id,'status':'CONFIRMADA','created':created}
