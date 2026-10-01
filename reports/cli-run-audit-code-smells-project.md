Agora vou compilar o relatório de auditoria com base na análise detalhada de todos os arquivos.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   25 analyzed | ~934 lines of code

## Summary
CRITICAL: 1 | HIGH: 0 | MEDIUM: 3 | LOW: 1

## Findings

### [CRITICAL] AP-05 Senhas sem hash seguro / autenticação fraca
File: services/usuario_service.py:16-23
Description: Fallback de comparação de senha em texto puro. Quando o hash armazenado não contém `$` (linha 17), o código faz comparação direta `armazenada == senha` (linha 20). Isso significa que, se houver senhas em texto puro no banco (de uma migração antiga), a autenticação as aceita via comparação literal — vulnerável a timing attacks e expõe o fato de que senhas plaintext ainda são aceitas.
Impact: Se o banco contiver senhas sem hash (cenário de migração), um atacante com acesso ao banco lê as senhas diretamente. A heurística `"$" in armazenada` pode falhar para hashes de outros formatos.
Recommendation: Remover o fallback de comparação plaintext. Forçar re-hash na migration/seed e usar apenas `check_password_hash` (PB-05).

### [MEDIUM] AP-11 Validação ausente / inconsistente
File: models/produto_model.py:29,32, utils/validators.py:55-58
Description: (1) Em `produto_model.py`, `if preco_min:` e `if preco_max:` usam teste de truthiness — o valor `0` (zero) é falsy em Python, então `preco_min=0` seria ignorado silenciosamente em vez de filtrar produtos com preço >= 0. (2) Em `validar_usuario`, o campo `email` aceita qualquer string não vazia sem validação de formato (nem mesmo um `@` é exigido).
Impact: (1) Bug funcional: busca com `preco_min=0` não aplica o filtro. (2) Dados inválidos no banco — emails sem formato correto.
Recommendation: (1) Usar `if preco_min is not None:` em vez de truthiness. (2) Adicionar validação básica de formato de email (PB-11).

### [MEDIUM] AP-14 Integridade de dados — constraints ausentes no schema
File: models/database.py:22-28, models/database.py:9-18
Description: A coluna `email` na tabela `usuarios` não tem constraint `UNIQUE`, permitindo cadastro de múltiplos usuários com o mesmo email. Colunas obrigatórias no nível da aplicação (`nome`, `preco`, `estoque` em `produtos`; `nome`, `email`, `senha` em `usuarios`) não têm `NOT NULL` no schema SQL.
Impact: Dados duplicados/nulos no banco que a aplicação assume não existirem; a validação da app pode ser contornada por acesso direto ao banco ou por seeds/migrations.
Recommendation: Adicionar `NOT NULL` nas colunas obrigatórias e `UNIQUE` em `usuarios.email` (PB-14).

### [MEDIUM] AP-01 Credenciais hardcoded (seed data)
File: models/seed.py:22-25
Description: Senhas de desenvolvimento em texto puro no código-fonte: `"admin123"`, `"123456"`, `"senha123"`. Embora sejam hasheadas antes da inserção no banco (linha 26), os valores plaintext ficam visíveis no repositório.
Impact: Senhas de exemplo fracas e previsíveis; se o seed rodar em produção, cria contas com credenciais conhecidas publicamente.
Recommendation: Documentar que o seed é apenas para desenvolvimento; considerar ler senhas de variáveis de ambiente ou gerar senhas aleatórias no seed (PB-01).

### [LOW] AP-18 Legibilidade — `id` sombreia built-in do Python
File: controllers/produto_controller.py:13,26,33, controllers/usuario_controller.py:13
Description: Os parâmetros de função usam o nome `id`, que sombreia a função built-in `id()` do Python. Ex.: `def buscar_produto(id):`, `def atualizar_produto(id):`, `def deletar_produto(id):`, `def buscar_usuario(id):`.
Impact: Risco baixo em termos práticos (a built-in `id()` raramente é usada), mas viola convenções de linting (PEP 8 / pylint W0622).
Recommendation: Renomear para `produto_id` / `usuario_id` conforme já usado em outras partes do código (ex.: `pedido_routes.py`) (PB-18).

================================
Total: 5 findings
================================
```

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
