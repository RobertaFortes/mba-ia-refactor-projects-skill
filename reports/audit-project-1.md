```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1, sqlite3 (stdlib)
Domain:        E-commerce API (produtos, usuários, pedidos, relatórios de vendas)
Architecture:  Monolítica em 4 arquivos planos (app.py, controllers.py, models.py, database.py). Existe uma divisão nominal controllers/models, mas models.py mistura SQL, regra de negócio e serialização de 4 domínios; app.py mistura rotas, endpoints admin e inicialização; conexão global singleton.
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido (SQLite, arquivo loja.db)
Endpoints:     19 routes mapped
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:7, controllers.py:289
Description: SECRET_KEY fixo como 'minha-chave-super-secreta-123' em app.config; o mesmo valor ainda é devolvido em texto puro pelo endpoint /health.
Impact: Qualquer pessoa com acesso ao repositório ou ao /health obtém a chave de sessão; a chave não pode ser rotacionada sem alterar o código.
Recommendation: Ler de variável de ambiente em um módulo config/settings e remover o campo da resposta do /health (PB-01, PB-08).

### [CRITICAL] AP-02 SQL Injection (SQL montado por concatenação)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Praticamente todas as queries concatenam entrada do usuário (ex.: "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'" no login; LIKE '%" + termo + "%' na busca; INSERT/UPDATE de produtos e usuários).
Impact: Bypass de login (' OR '1'='1), leitura, alteração e destruição arbitrária de dados.
Recommendation: Usar placeholders (?) com parâmetros em todas as queries; allowlist para partes dinâmicas (PB-02).

### [CRITICAL] AP-04 Dangerous Admin/Debug Endpoints
File: app.py:47-57, app.py:59-80, app.py:8, app.py:88, controllers.py:285-290
Description: POST /admin/query executa qualquer SQL recebido no corpo; POST /admin/reset-db apaga todas as tabelas; ambos sem autenticação. DEBUG=True fixo (app.py:8 e debug=True em app.py:88, com host 0.0.0.0). /health expõe db_path, debug e secret_key.
Impact: Qualquer cliente de rede pode ler/alterar/apagar o banco e, com o debugger do Flask exposto, executar código no servidor.
Recommendation: Remover /admin/query, proteger /admin/reset-db com token + flag de ambiente, DEBUG via config e enxugar o /health (PB-08, PB-01).

### [CRITICAL] AP-05 Senhas em texto puro / autenticação fraca
File: database.py:31, database.py:75-79, models.py:109-111, models.py:126-129
Description: A coluna senha guarda a senha em texto puro (seeds "admin123", "123456", "senha123"); o login compara texto puro direto no SQL; criar_usuario grava a senha recebida sem hash.
Impact: Um vazamento do banco expõe todas as senhas; contas comprometidas em outros serviços.
Recommendation: Hash salgado (werkzeug.security) na criação e check_password_hash no login; seeds já com hash (PB-06).

### [CRITICAL] AP-03 God File (sem separação de camadas)
File: models.py:1-314, app.py:1-88
Description: models.py concentra queries SQL, regras de negócio (cálculo de total/estoque em criar_pedido, desconto em relatorio_vendas), serialização e 4 domínios diferentes (produtos, usuários, pedidos, relatórios). app.py mistura registro de 19 rotas, lógica administrativa com SQL direto e bootstrap.
Impact: Impossível testar em isolamento; qualquer mudança afeta tudo; não existe camada de rotas/views nem de configuração.
Recommendation: Separar em config, models por domínio, controllers, routes, middlewares e entry point (PB-03).

### [HIGH] AP-06 Regra de negócio fora do lugar (controllers e models)
File: controllers.py:24-58, controllers.py:64-93, controllers.py:188-220, controllers.py:237-255, models.py:133-169, models.py:256-262
Description: Controllers validam e disparam notificações simuladas (ENVIANDO EMAIL/SMS/PUSH) e decidem efeitos de mudança de status; o model faz cálculo de total, checagem/baixa de estoque e regra de desconto por faixa de faturamento.
Impact: Lógica de negócio presa a camadas erradas; não reutilizável nem testável sem HTTP/banco.
Recommendation: Controllers só orquestram; regras vão para services/models de domínio; notificações em um serviço próprio (PB-04).

### [HIGH] AP-07 Estado global mutável / acoplamento sem injeção
File: database.py:4-12, database.py:86, models.py:1 (todas as funções chamam get_db()), controllers.py:3, controllers.py:266
Description: db_connection é uma variável global mutável criada por get_db() com check_same_thread=False; models e controllers (health_check) dependem diretamente dela; o schema e o seed são executados dentro do get_db().
Impact: Conexão compartilhada entre threads, testes que vazam estado, impossível trocar o banco.
Recommendation: Factory da aplicação + conexão por contexto/request (ou injetada), com init_db separado (PB-05).

### [HIGH] AP-08 Dados sensíveis expostos nas respostas
File: models.py:83, models.py:99, controllers.py:130-132, controllers.py:289, controllers.py:11-12
Description: GET /usuarios e GET /usuarios/<id> devolvem o campo senha; /health devolve secret_key; handlers devolvem str(e) das exceções ao cliente.
Impact: Vazamento de credenciais e detalhes internos.
Recommendation: Serializer público sem senha e handler de erros que devolve mensagem genérica em 500 (PB-07, PB-10).

### [MEDIUM] AP-10 Queries N+1
File: models.py:171-201, models.py:203-233
Description: Para cada pedido é feita uma query de itens e, para cada item, outra query de produto (cursor2/cursor3 aninhados).
Impact: Número de queries cresce com pedidos x itens; lentidão em volume real.
Recommendation: Uma query com JOIN (pedidos, itens_pedido, produtos) agrupada em memória, preservando "Desconhecido" para produto ausente (PB-09).

### [MEDIUM] AP-11 Validação inconsistente/ausente
File: controllers.py:24-58, controllers.py:64-93, controllers.py:167-171, controllers.py:239-243, controllers.py:118-121
Description: O PUT de produto não valida tamanho do nome nem categoria (o POST valida); preco/estoque não têm checagem de tipo (string quebra a comparação <0 e vira 500); login acessa dados.get sem checar corpo nulo; preco_min/preco_max com float() sem tratamento; atualizar status assume corpo JSON.
Impact: 500 em entradas inválidas e regras divergentes entre criação e atualização.
Recommendation: Validators reutilizáveis usados por POST e PUT, lançando erros de domínio (PB-10).

### [MEDIUM] AP-12 Tratamento de erros repetido e não centralizado
File: controllers.py:6-12, controllers.py:14-22, controllers.py:60-62 (padrão repetido em todos os 17 handlers), app.py:75-80
Description: Cada handler repete try/except Exception devolvendo str(e) com 500; não há error handler global.
Impact: Duplicação, mensagens internas vazando, formato de erro inconsistente.
Recommendation: Exceções de domínio + errorhandler global (PB-10).

### [MEDIUM] AP-13 Duplicação de código
File: models.py:12-21, models.py:31-40, models.py:304-312, models.py:177-199, models.py:211-231, models.py:79-86, models.py:95-102
Description: O dict de produto é montado campo a campo em 3 lugares, o de usuário em 2; get_pedidos_usuario e get_todos_pedidos são praticamente idênticas.
Impact: Mudanças de schema exigem editar vários pontos; risco de divergência.
Recommendation: Serializers/mappers únicos por entidade e função compartilhada de montagem de pedidos (PB-07, PB-09).

### [MEDIUM] AP-14 Operação multi-etapa sem transação e sem restauração de estoque
File: models.py:133-169, models.py:275-283, controllers.py:247-250
Description: criar_pedido faz INSERT de pedido, itens e UPDATE de estoque sem rollback em falha; cancelar um pedido apenas imprime "Devolver estoque" mas não devolve; deletar produto não considera itens de pedido.
Impact: Estado inconsistente do estoque e de pedidos parciais.
Recommendation: Transação atômica com rollback e devolução de estoque no cancelamento (PB-15).

### [LOW] AP-16 Magic numbers e strings
File: models.py:256-262, controllers.py:52, controllers.py:242, app.py:88, controllers.py:287
Description: Faixas de desconto 10000/5000/1000 e taxas 0.1/0.05/0.02, listas de categorias e status, porta 5000 e versão "1.0.0" soltas no código.
Impact: Regras de negócio escondidas e duplicáveis.
Recommendation: Constantes nomeadas em config/constants (PB-13).

### [LOW] AP-17 Logging com print
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250, app.py:56, app.py:83-86
Description: print() usado como log e como "envio" de e-mail/SMS/push simulado; loga e-mail de usuário em login.
Impact: Sem níveis de log e sem controle de saída.
Recommendation: logging + notification service (PB-14).

### [LOW] AP-18 Legibilidade e código morto
File: models.py:2, database.py:2, models.py:24, models.py:65, models.py:89, controllers.py:14, controllers.py:98, models.py:187-192
Description: Imports não usados (sqlite3 em models.py, os em database.py); parâmetro id sombreia o builtin; cursor2/cursor3 sem significado.
Impact: Ruído e confusão na leitura.
Recommendation: Remover imports mortos, renomear variáveis (PB-16).

Deprecated API scan: nenhuma API deprecated relevante encontrada (Flask 3.1.1 / sqlite3 stdlib). O uso fixo de debug=True foi reportado em AP-04.

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
