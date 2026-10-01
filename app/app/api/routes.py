from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.db import init_db, connect
from app.core.config import APP_VERSION
from app.models.schemas import UserIn, ContactIn, CaseIn, CaseStatusIn, TransactionIn, EventIn, DocumentIn
from app.models.interpretation import InterpretIn, ConfirmIn
from app.services.interpreter import propose, confirm
from app.services.cases import create_case,list_cases,update_status
from app.services.finance import create_transaction,list_transactions,summary
from app.services.events import create_event
from app.services.contacts import create_contact,list_contacts
from app.services.documents import create_document,list_documents
from app.services.memory import memory,case_memory
from app.services.reports import pdf_report,excel_report
from app.core.utils import new_id,now_iso

router=APIRouter(); init_db()

@router.get('/health')
def health(): return {'ok':True,'service':'resolve','version':APP_VERSION}

@router.post('/users')
def create_user(data:UserIn):
    uid=new_id('usr'); now=now_iso()
    with connect() as conn:
        conn.execute('INSERT INTO users(id,name,created_at) VALUES(?,?,?)',(uid,data.name,now)); conn.commit()
    return {'id':uid,'name':data.name,'created_at':now}


@router.post('/interpret')
def interpret(data: InterpretIn):
    result=propose(data.user_id,data.text)
    if data.execute and result['proposal']['confidence'] >= 0.85:
        result['execution']=confirm(result['interpretation_id'])
    else:
        result['execution']=None
    return result

@router.post('/interpret/confirm')
def interpret_confirm(data: ConfirmIn):
    result=confirm(data.interpretation_id)
    if not result: raise HTTPException(404,'Interpretação não encontrada')
    return result

@router.post('/contacts')
def post_contact(data:ContactIn): return create_contact(data)

@router.get('/contacts/{user_id}')
def get_contacts(user_id:str): return list_contacts(user_id)

@router.post('/cases')
def post_case(data:CaseIn): return create_case(data)

@router.get('/cases/{user_id}')
def get_cases(user_id:str,status:str|None=None): return list_cases(user_id,status)

@router.get('/case/{case_id}/memory')
def get_case_memory(case_id:str):
    item=case_memory(case_id)
    if not item: raise HTTPException(404,'Caso não encontrado')
    return item

@router.patch('/cases/{case_id}/status')
def patch_case_status(case_id:str,data:CaseStatusIn):
    item=update_status(case_id,data.status)
    if not item: raise HTTPException(404,'Caso não encontrado')
    return item

@router.post('/finance/transactions')
def post_transaction(data:TransactionIn): return create_transaction(data)

@router.get('/finance/transactions/{user_id}')
def get_transactions(user_id:str,kind:str|None=None): return list_transactions(user_id,kind)

@router.get('/finance/summary/{user_id}')
def get_summary(user_id:str): return summary(user_id)

@router.post('/events')
def post_event(data:EventIn): return create_event(data)

@router.post('/documents')
def post_document(data:DocumentIn): return create_document(data)

@router.get('/documents/{user_id}')
def get_documents(user_id:str,case_id:str|None=None): return list_documents(user_id,case_id)

@router.get('/memory/{user_id}')
def get_memory(user_id:str): return memory(user_id)

@router.get('/reports/summary/{user_id}')
def report_summary(user_id:str):
    s,t,c=summary(user_id),list_transactions(user_id),list_cases(user_id)
    return {'summary':s,'transaction_count':len(t),'case_count':len(c),'memory':memory(user_id)}

@router.get('/reports/{user_id}/pdf')
def report_pdf(user_id:str):
    data=pdf_report(user_id); return Response(data,media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="resolve_relatorio.pdf"'})

@router.get('/reports/{user_id}/excel')
def report_excel(user_id:str):
    data=excel_report(user_id); return Response(data,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="resolve_relatorio.xlsx"'})
