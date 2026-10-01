# RESOLVE 2.0 — notas de produção

Esta versão adiciona relacionamentos entre contato, caso, evento, movimentação financeira e documento.

## Importante

O SQLite é adequado para desenvolvimento/testes locais. Antes de uso multiusuário em produção, migrar para PostgreSQL ou armazenamento persistente gerenciado.

A tabela `documents` nesta etapa guarda metadados e uma referência opcional (`storage_ref`); o upload físico do arquivo será implementado na etapa de documentos.

A camada de IA deve apenas interpretar e propor estrutura. Cálculos financeiros, persistência, permissões e auditoria permanecem determinísticos no backend.
