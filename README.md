# RESOLVE 2.0 — CORE + PAINEL + IA opcional

Versão de staging para o RESOLVE 2.0.

## Arquitetura
- FastAPI
- SQLite por padrão (`data/resolve.db`)
- Painel web em `/`
- Memória, casos, eventos, financeiro, documentos e relatórios
- PDF e Excel
- Interpretador local
- OpenAI opcional via `OPENAI_API_KEY`

## Regra central
IA interpreta → sistema valida → usuário confirma → sistema registra.

## Execução
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

## Docker
```bash
docker build -t resolve-2 .
docker run -p 8787:8787 resolve-2
```

## Endpoints principais
- `GET /`
- `GET /health`
- `POST /users`
- `POST /interpret`
- `POST /interpret/confirm`
- `GET /memory/{user_id}`
- `GET /finance/summary/{user_id}`
- `GET /reports/{user_id}/pdf`
- `GET /reports/{user_id}/excel`
- `GET /docs`
