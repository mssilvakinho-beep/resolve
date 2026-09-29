# RESOLVE — Produção 1.0

Ponte do laboratório para um servidor real.

Inclui FastAPI, PostgreSQL, Docker Compose e OpenAI Responses API.

Subida:
1. Copie `.env.example` para `.env`.
2. Preencha os segredos.
3. `docker compose up --build`
4. Teste `/health`.

Para WhatsApp real ainda é necessário configurar o aplicativo/Business Manager,
número comercial, credenciais e webhook HTTPS na Meta. O endpoint preparado é
`POST /webhook/whatsapp`.

Nunca coloque OPENAI_API_KEY no navegador ou código público.
