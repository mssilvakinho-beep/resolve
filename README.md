# RESOLVE 2.0 CORE

Núcleo operacional do RESOLVE: memória, casos, financeiro, documentos, relatórios e interpretação controlada.

## O que esta versão entrega
- Usuários, contatos e casos.
- Eventos, documentos e movimentações financeiras relacionados aos casos.
- Memória global e memória detalhada por caso.
- Relatórios PDF e Excel.
- Interpretador PT-BR determinístico como camada de segurança/fallback.
- Fluxo **interpretar → propor → confirmar → registrar**.
- Endpoint `/interpret` para transformar linguagem natural em proposta estruturada.
- Endpoint `/interpret/confirm` para executar somente após confirmação explícita.
- OpenAI preparada como dependência para a próxima etapa; a interpretação local continua funcionando sem chave.

## Regra de segurança
O interpretador não deve executar ações externas. A proposta é persistida como `PENDENTE` e só vira registro após confirmação, salvo quando um modo de execução explicitamente autorizado atingir o nível de confiança definido.

## Rodar localmente
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger: `/docs`

## Testes
```bash
pytest -q
```

## Próxima camada
Conectar o interpretador ao modelo da OpenAI para melhorar compreensão de linguagem natural, mantendo o backend como responsável por validação, regras, cálculos, persistência e auditoria.
