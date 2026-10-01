from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_interpret_then_confirm():
    uid=client.post('/users',json={'name':'Usuário IA'}).json()['id']
    r=client.post('/interpret',json={'user_id':uid,'text':'Fechei um serviço com João por R$ 3.500 e comprei material por R$ 800.'})
    assert r.status_code==200
    data=r.json(); assert data['status']=='PENDENTE'; assert data['proposal']['revenue']==3500; assert data['proposal']['expense']==800
    c=client.post('/interpret/confirm',json={'interpretation_id':data['interpretation_id']})
    assert c.status_code==200; assert c.json()['status']=='CONFIRMADA'
    mem=client.get(f'/memory/{uid}').json(); assert len(mem['transactions'])==2
