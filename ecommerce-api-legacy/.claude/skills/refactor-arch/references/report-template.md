# Template do Relatório de Auditoria (Fase 2)

O relatório deve seguir **exatamente** esta estrutura. Substitua os `<...>`; não adicione seções extras antes da pergunta de confirmação.

## Regras de preenchimento

- `Files`: quantidade de arquivos-fonte analisados (a mesma da Fase 1) e linhas aproximadas.
- `Summary`: contagem de findings por severidade; a soma deve bater com `Total`.
- Ordem dos findings: **CRITICAL → HIGH → MEDIUM → LOW**. Dentro da mesma severidade, do mais impactante para o menos.
- Cada finding tem: severidade + nome do anti-pattern (com ID do catálogo), `File` com **caminho e linhas exatos** (`arquivo.ext:10-25`; múltiplos locais separados por vírgula), `Description` (o que foi visto, citando o trecho relevante), `Impact` (consequência concreta) e `Recommendation` (correção alinhada ao playbook, citando o padrão `PB-xx`).
- Findings de API deprecated usam o nome `Deprecated API` e citam a API antiga e a substituta.
- Linhas precisam ter sido conferidas lendo o arquivo. Nunca use intervalos aproximados como `1-350` se o problema é localizado.
- Findings agrupados: quando o mesmo anti-pattern ocorre em vários pontos, uma única entrada com `File:` listando cada local.
- Mínimo 5 findings e ao menos 1 CRITICAL ou HIGH (desde que existam de verdade no código).

## Formato

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <AP-xx> <Nome do anti-pattern>
File: <arquivo>:<linhas>[, <arquivo>:<linhas>]
Description: <o que foi encontrado, com o trecho/valor relevante>
Impact: <consequência>
Recommendation: <correção, PB-xx>

### [HIGH] <AP-xx> <Nome do anti-pattern>
File: ...
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] ...

### [LOW] ...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Exemplo (trecho ilustrativo)

```
### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123' em app.config.
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões; a chave não pode ser rotacionada sem alterar o código.
Recommendation: Ler de variável de ambiente em um módulo config/settings (PB-01).

### [MEDIUM] AP-15 Deprecated API
File: models/task.py:15-16, routes/task_routes.py:42,51,67
Description: `datetime.utcnow()` (deprecated no Python 3.12) e `Model.query.get()` (API legada do SQLAlchemy 2.x).
Impact: DeprecationWarning hoje, remoção em versões futuras.
Recommendation: `datetime.now(timezone.utc)` e `db.session.get(Model, id)` (PB-12).
```
