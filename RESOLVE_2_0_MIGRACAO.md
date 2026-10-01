# RESOLVE 2.0 — migração controlada para Blitz

## Estado verificado no código
- FastAPI com painel, interpretador, contatos, casos, eventos, transações, memória e relatórios PDF/Excel.
- Dockerfile inicia `uvicorn app.main:app` na porta `${PORT:-8787}`.
- Banco de dados atual: SQLite. Arquivos `data/resolve.db` de demonstração NÃO são distribuídos no pacote de publicação.
- O endpoint `/interpret` aceita `execute=true` e pode confirmar automaticamente propostas com confiança >= 0,85; isso deve ser desabilitado antes de exposição pública.
- As rotas de usuário, memória, finanças e relatórios não exigem autenticação; NÃO publicar publicamente com dados reais.
- A tabela de documentos contém metadados/referências, não upload físico completo.

## Migração segura
1. Preservar o app RESOLVE 1.7 online e fazer backup dos dados atuais antes de qualquer substituição.
2. Criar branch `resolve-2.0` no GitHub e enviar o código do pacote para essa branch; não substituir a branch principal.
3. Adicionar autenticação e autorização por usuário a TODAS as rotas de dados; bloquear confirmação automática e adicionar validação de pertencimento de caso, contato e transação.
4. Migrar SQLite para armazenamento persistente adequado (ex.: PostgreSQL gerenciado), com backup e migrações versionadas.
5. Criar um segundo app Blitz privado/de homologação, vinculado à branch `resolve-2.0`; configurar segredos apenas nas variáveis do provedor.
6. Rodar testes de isolamento entre usuários, persistência após reinício, fluxo de confirmação, cálculos, PDF e Excel.
7. Só então considerar a substituição gradual do app principal e conectar a API OpenAI com crédito.

## Primeira ação agora
No GitHub, criar a branch `resolve-2.0` a partir da `main`. Enviar print da branch criada; depois enviaremos os arquivos limpos da 2.0 sem tocar na versão 1.7.
