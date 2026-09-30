```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  sqlite3 ^5.1.6
Domain:        LMS API (cursos, matrículas, pagamentos) com fluxo de checkout e relatório financeiro
Architecture:  Monolítica — uma God Class (AppManager) concentra schema/seed do banco, registro de rotas, regra de negócio e acesso a dados; utils.js mistura config com segredos, cache global e "criptografia"; app.js é só o bootstrap.
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite em memória)
Endpoints:     3 routes mapped
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: src/utils.js:1-7
Description: O objeto config guarda dbUser "admin_master", dbPass "senha_super_secreta_prod_123", paymentGatewayKey "pk_live_1234567890abcdef" (chave live) e smtpUser em texto no código.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de produção e a chave do gateway de pagamento; impossível rotacionar sem novo deploy.
Recommendation: Ler tudo de process.env em src/config/settings.js e documentar em .env.example (PB-01).

### [CRITICAL] AP-03 God Class (sem separação de camadas)
File: src/AppManager.js:4-141
Description: A classe AppManager cria o banco (linhas 7, 10-23), popula seeds, registra as 3 rotas (25-138), executa SQL, valida entrada, processa pagamento e grava auditoria — tudo no mesmo arquivo. Não há models, controllers, routes nem config separados.
Impact: Impossível testar em isolamento; toda mudança afeta tudo; nenhuma camada tem responsabilidade única.
Recommendation: Quebrar em config, models (database + um por entidade), services (pagamento/cache), controllers, routes e middlewares, deixando app.js como composition root (PB-03).

### [CRITICAL] AP-04 Endpoints administrativos sem autenticação
File: src/AppManager.js:80, src/AppManager.js:131-137
Description: GET /api/admin/financial-report (dados de alunos e receita) e DELETE /api/users/:id (remove qualquer usuário) não têm nenhuma checagem de autenticação/autorização.
Impact: Qualquer cliente de rede lê o relatório financeiro e apaga usuários.
Recommendation: Middleware de autorização por token administrativo vindo de config (PB-08).

### [CRITICAL] AP-05 Criptografia caseira e senhas fracas
File: src/utils.js:17-23, src/AppManager.js:68, src/AppManager.js:18
Description: badCrypto gera o "hash" concatenando 10.000 vezes 2 caracteres de base64 da senha e cortando em 10 caracteres — reversível/colidível e sem salt. Usuários criados no checkout recebem senha padrão "123456" quando pwd não é enviado; o usuário de seed guarda '123' em texto puro.
Impact: Senhas trivialmente recuperáveis; contas com senha padrão previsível.
Recommendation: Hash com crypto.scryptSync + salt aleatório e verificação em tempo constante; seed já com hash (PB-06).

### [HIGH] AP-06 Regra de negócio dentro do handler da rota
File: src/AppManager.js:28-78
Description: O handler do checkout valida campos, busca curso, decide criar usuário, "processa" o pagamento (cc.startsWith("4") na linha 46), cria matrícula, pagamento e log de auditoria e atualiza cache.
Impact: Regra de pagamento/matrícula não reutilizável nem testável sem HTTP e banco.
Recommendation: Controller orquestra; um service de checkout/pagamento concentra a regra; models fazem só acesso a dados (PB-04).

### [HIGH] AP-07 Estado global mutável e acoplamento sem injeção
File: src/utils.js:9-15, src/utils.js:25, src/AppManager.js:2, src/AppManager.js:7
Description: globalCache e totalRevenue são variáveis de módulo mutáveis exportadas; AppManager instancia o banco no próprio construtor e importa utils diretamente; totalRevenue nunca é usado de fato.
Impact: Estado vaza entre requisições/testes; impossível trocar banco ou cache.
Recommendation: CacheService encapsulado e conexão criada no entry point e injetada (PB-05).

### [HIGH] AP-09 Callback hell e fluxo assíncrono frágil
File: src/AppManager.js:37-77, src/AppManager.js:83-127
Description: O checkout aninha 5 níveis de callbacks; o relatório financeiro controla conclusão com contadores manuais (coursesPending, enrPending) e pode nunca responder se algum callback falhar (err ignorado em 92-93, 104-106).
Impact: Race conditions, respostas perdidas/duplicadas, crash quando enrollments é undefined.
Recommendation: Helpers com Promises e async/await, Promise.all onde couber (PB-11).

### [HIGH] AP-17 Log de dados sensíveis
File: src/AppManager.js:45
Description: console.log imprime o número completo do cartão e a chave do gateway de pagamento.
Impact: Vazamento de dado de cartão (PCI) e de segredo em logs.
Recommendation: Nunca logar cartão/chaves; se preciso, mascarar (****1234) (PB-14).

### [MEDIUM] AP-10 Queries N+1
File: src/AppManager.js:83-127
Description: O relatório financeiro consulta matrículas por curso e, para cada matrícula, faz 2 queries (usuário e pagamento).
Impact: Número de queries cresce com cursos x matrículas.
Recommendation: Uma query com JOIN (courses, enrollments, users, payments) agrupada em memória (PB-09).

### [MEDIUM] AP-11 Validação de entrada insuficiente
File: src/AppManager.js:29-35
Description: O checkout só verifica presença de usr, eml, c_id e card; não valida formato de e-mail, tipo do curso ou do cartão; pwd é opcional e cai na senha padrão.
Impact: Dados inválidos chegam ao banco e ao "gateway".
Recommendation: Validador central com mensagens claras (PB-10).

### [MEDIUM] AP-12 Erros ignorados e sem tratamento centralizado
File: src/AppManager.js:38, src/AppManager.js:57-61, src/AppManager.js:133-136, src/app.js:6-14
Description: Erros de callbacks são ignorados (o log de auditoria e o DELETE respondem sucesso mesmo se err); respostas de erro são texto solto (send("Erro DB")) em formatos diferentes; não há middleware de erro no Express.
Impact: Falhas silenciosas e respostas inconsistentes.
Recommendation: Erros de domínio + middleware final (err, req, res, next) (PB-10).

### [MEDIUM] AP-14 Integridade de dados / operações sem transação
File: src/AppManager.js:66-72, src/AppManager.js:50-63, src/AppManager.js:131-137
Description: O usuário é criado (69-72) antes da aprovação do pagamento (48), deixando usuário órfão quando o cartão é recusado; matrícula, pagamento e auditoria são inserts separados sem transação; o DELETE de usuário deixa matrículas e pagamentos órfãos (a própria mensagem da linha 135 admite).
Impact: Dados inconsistentes e lixo no banco.
Recommendation: Ordem correta (pagamento antes do cadastro), transação BEGIN/COMMIT/ROLLBACK e remoção em cascata na mesma transação (PB-15).

### [LOW] AP-16 Magic numbers e strings
File: src/AppManager.js:46, src/AppManager.js:48, src/utils.js:19-22, src/utils.js:6
Description: Prefixo de cartão "4", status "PAID"/"DENIED", 10000 iterações, substring(0, 10), porta 3000 soltos.
Impact: Regras de negócio escondidas.
Recommendation: Constantes nomeadas em config (PB-13).

### [LOW] AP-17 console.log como log
File: src/utils.js:13, src/app.js:13
Description: Logs de cache e de startup via console.log sem níveis.
Impact: Sem controle de saída.
Recommendation: Logger simples e mensagens sem dados sensíveis (PB-14).

### [LOW] AP-18 Nomes ruins e código morto
File: src/AppManager.js:29-33, src/AppManager.js:26, src/AppManager.js:2, src/utils.js:10, src/utils.js:25
Description: Variáveis u, e, p, cid, cc; alias self; imports/exports não usados (totalRevenue, badCrypto duplica responsabilidade); nomes de contrato (usr, eml, pwd, c_id, card) usados diretamente na lógica.
Impact: Leitura difícil.
Recommendation: Nomes claros mapeados a partir do corpo (mantendo o contrato) (PB-16).

Deprecated API scan: nenhuma API deprecated encontrada (sem new Buffer, var, request, body-parser; Buffer.from é o correto).

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
