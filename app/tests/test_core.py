from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['ok'] is True

def test_end_to_end_memory_and_finance():
    user=client.post('/users',json={'name':'Teste 2.0'}).json(); uid=user['id']
    contact=client.post('/contacts',json={'user_id':uid,'name':'João','kind':'cliente'}).json(); cid=contact['id']
    case=client.post('/cases',json={'user_id':uid,'contact_id':cid,'title':'Instalação de câmeras'}).json(); case_id=case['id']
    client.post('/finance/transactions',json={'user_id':uid,'case_id':case_id,'contact_id':cid,'kind':'RECEITA','category':'SERVIÇO','description':'Instalação','amount':3500,'paid':True})
    client.post('/finance/transactions',json={'user_id':uid,'case_id':case_id,'contact_id':cid,'kind':'DESPESA','category':'MATERIAL','description':'Câmeras e cabos','amount':800,'paid':True})
    client.post('/events',json={'user_id':uid,'case_id':case_id,'contact_id':cid,'type':'NOTA','description':'Serviço agendado'})
    client.post('/documents',json={'user_id':uid,'case_id':case_id,'contact_id':cid,'filename':'orcamento.pdf','document_type':'orcamento'})
    mem=client.get(f'/memory/{uid}').json(); assert len(mem['cases'])==1; assert len(mem['transactions'])==2; assert len(mem['documents'])==1
    detail=client.get(f'/case/{case_id}/memory').json(); assert detail['receitas']==3500; assert detail['despesas']==800; assert detail['saldo_registrado']==2700

def test_actions_are_not_needed_for_deterministic_core():
    r=client.get('/finance/summary/nonexistent'); assert r.status_code==200
