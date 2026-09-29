import os
from fastapi import FastAPI, Request, HTTPException
from openai import OpenAI

app=FastAPI(title="RESOLVE API",version="production-1.0")
MODEL=os.getenv("OPENAI_MODEL","gpt-5.6-luna")

@app.get("/health")
def health():
    return {"ok":True,"service":"resolve","model":MODEL}

@app.post("/webhook/whatsapp")
async def whatsapp(request: Request):
    payload=await request.json()
    text=payload.get("text"); sender=payload.get("sender")
    if not text or not sender:
        raise HTTPException(400,"sender e text são obrigatórios")
    return await interpret(sender,text)

@app.post("/interpret")
async def interpret(sender: str, text: str):
    client=OpenAI()
    response=client.responses.create(
        model=MODEL,
        instructions="""Você é o cérebro interpretador do RESOLVE.
Interprete mensagens em português do Brasil.
Não execute ações. Não invente fatos.
Quando identidade, dinheiro ou ação externa estiverem ambíguos, peça esclarecimento.
Retorne uma resposta curta e útil ao usuário.""",
        input=text
    )
    return {"sender":sender,"reply":response.output_text,"model":MODEL}
