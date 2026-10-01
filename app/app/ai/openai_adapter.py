import json, os

SYSTEM = '''Você é o interpretador do RESOLVE. Interprete português do Brasil e retorne SOMENTE JSON válido.
Schema: {"intent":"RECEITA|DESPESA|MOVIMENTO_MISTO|NOVO_CASO|NOTA|INDETERMINADO","confidence":0.0,"contact_name":null,"case_title":null,"revenue":null,"expense":null,"expense_category":null,"due_date":null,"notes":null}
Não invente fatos. Valores devem ser números em reais. Se houver ambiguidade relevante, reduza confidence e explique em notes. Não execute ações.'''

def available():
    return bool(os.getenv('OPENAI_API_KEY'))

def interpret_with_openai(text: str) -> dict:
    from openai import OpenAI
    client=OpenAI()
    model=os.getenv('OPENAI_MODEL','gpt-5.6-luna')
    r=client.responses.create(model=model, instructions=SYSTEM, input=text)
    raw=r.output_text.strip()
    if raw.startswith('```'):
        raw=raw.strip('`')
        if raw.startswith('json'): raw=raw[4:].strip()
    data=json.loads(raw)
    data['confidence']=max(0.0,min(float(data.get('confidence',0)),1.0))
    return data
