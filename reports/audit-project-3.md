```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0 (marshmallow, requests e python-dotenv declaradas mas não usadas)
Domain:        Task Manager API (tasks, usuários, categorias, relatórios)
Architecture:  Parcialmente em camadas — existem models/, routes/, services/ e utils/, mas as rotas concentram validação, regra de negócio e acesso ao ORM (não há camada de controllers); services e utils contêm código morto; config e segredos estão no app.py.
Source files:  13 files analyzed (~1158 lines)
DB tables:     tasks, users, categories (SQLite via SQLAlchemy, tasks.db)
Endpoints:     22 routes mapped
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   13 analyzed | ~1158 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:13, services/notification_service.py:9-10
Description: SECRET_KEY fixa 'super-secret-key-123' no app.py; usuário e senha SMTP ('taskmanager@gmail.com' / 'senha123') fixos no NotificationService.
Impact: Segredos expostos no repositório; a chave não pode ser rotacionada sem alterar código.
Recommendation: Ler de variáveis de ambiente em config/settings.py e documentar em .env.example (PB-01).

### [CRITICAL] AP-04 Modo debug ativo em 0.0.0.0
File: app.py:34
Description: app.run(debug=True, host='0.0.0.0', port=5000) fixo no código.
Impact: O debugger interativo do Werkzeug exposto na rede permite execução remota de código.
Recommendation: DEBUG e HOST vindos de configuração, desligado por padrão (PB-01, PB-12).

### [CRITICAL] AP-05 Hash fraco, token falso e ausência de autorização
File: models/user.py:29, models/user.py:32, routes/user_routes.py:210, routes/user_routes.py:52, routes/user_routes.py:71-78, routes/user_routes.py:119-122, routes/user_routes.py:134-151
Description: Senhas guardadas com MD5 sem salt; o login devolve o token 'fake-jwt-token-' + id (previsível, sem assinatura); nenhuma rota exige autenticação: qualquer um cria usuário com role 'admin' no POST /users, altera roles no PUT e deleta usuários (e suas tasks).
Impact: Senhas quebráveis por tabela; contas forjáveis; escalonamento de privilégio trivial.
Recommendation: werkzeug.security para hash salgado; token assinado (itsdangerous) e decorators de autenticação/autorização para rotas de escrita sensíveis; role só concedida por admin (PB-06).

### [HIGH] AP-08 Hash de senha exposto nas respostas
File: models/user.py:16-25, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: User.to_dict() inclui 'password' (o hash MD5) e é devolvido em GET /users/<id>, POST /users, PUT /users/<id> e /login.
Impact: Vazamento de credenciais a qualquer cliente.
Recommendation: Serializer público sem o campo password (PB-07).

### [HIGH] AP-06 Regra de negócio e acesso a dados dentro das rotas (sem controllers)
File: routes/task_routes.py:12-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:273-299, routes/report_routes.py:12-100, routes/report_routes.py:103-154, routes/user_routes.py:134-151, routes/report_routes.py:157-223
Description: Os handlers validam entrada, consultam o ORM, calculam atraso (overdue), estatísticas e taxas de conclusão e fazem cascade manual de tasks; não existe camada de controllers/services. O report_routes ainda hospeda o CRUD de categorias, responsabilidade que não é de relatórios.
Impact: Rotas gigantes (até ~95 linhas), impossíveis de testar sem HTTP; responsabilidades misturadas.
Recommendation: Criar controllers por domínio (task, user, category, report), mover regras para models/services e reduzir as rotas a mapeamento URL -> controller (PB-04, PB-03).

### [HIGH] AP-06 Camada de models anêmica e services/utils mortos
File: models/task.py:38-60, utils/helpers.py:57-108, services/notification_service.py:4-48
Description: Task.is_overdue(), validate_status() e validate_priority() existem e nunca são usados (as rotas recalculam à mão); utils/helpers.process_task_data() (validação completa) nunca é chamada; NotificationService nunca é instanciado nem usado.
Impact: Duas implementações da mesma regra, uma delas morta; a arquitetura em camadas existe só no papel.
Recommendation: Ligar as camadas: rotas -> controllers -> services/models, removendo o que estiver morto (PB-04, PB-16).

### [HIGH] AP-07 Efeito colateral e configuração no import do módulo
File: app.py:11-13, app.py:30-31, services/notification_service.py:6-10
Description: Configuração fixa e db.create_all() executados no import do módulo app (o seed.py importa app); NotificationService lê host/porta/credenciais fixos no próprio construtor, sem injeção.
Impact: Difícil testar/alterar configuração; acoplamento a valores globais.
Recommendation: create_app(settings) como composition root, config/settings.py, serviços recebendo config (PB-05).

### [MEDIUM] AP-10 Queries N+1
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:56-71, routes/report_routes.py:163
Description: GET /tasks faz User.query.get e Category.query.get para cada task; GET /users chama len(u.tasks) (lazy load) para cada usuário; /reports/summary consulta as tasks de cada usuário em loop; GET /categories conta tasks por categoria em loop.
Impact: Queries crescem com o volume de dados.
Recommendation: joinedload/eager loading e agregações com GROUP BY (PB-09).

### [MEDIUM] AP-13 Duplicação de código
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/user_routes.py:171-180, routes/report_routes.py:33-43, routes/report_routes.py:130-136, routes/task_routes.py:17-28, routes/user_routes.py:162-169, routes/user_routes.py:15-24
Description: O cálculo de "atrasada" aparece 6 vezes apesar de Task.is_overdue(); a serialização de task é montada campo a campo em rotas em vez de usar Task.to_dict(); regras de validação de task repetidas entre criar e atualizar.
Impact: Correções precisam ser feitas em vários pontos; comportamentos divergem.
Recommendation: Um único is_overdue/serializer no model e validators compartilhados (PB-07, PB-10).

### [MEDIUM] AP-11 Validação inconsistente/ausente
File: routes/task_routes.py:113, routes/task_routes.py:182, routes/task_routes.py:261-264, routes/report_routes.py:152-154, routes/user_routes.py:61, routes/user_routes.py:106, routes/user_routes.py:64, routes/user_routes.py:115
Description: Comparações de prioridade sem checar tipo (priority "a" causa 500); int(priority)/int(user_id) sem tratamento na busca; update_category não trata corpo nulo (data['name'] em None); a regex de e-mail e o tamanho mínimo de senha são copiados em vários pontos; a data aceita apenas YYYY-MM-DD nas rotas, enquanto helpers aceita dois formatos.
Impact: 500 em entrada inválida e regras divergentes.
Recommendation: Validators únicos e erros 400 padronizados (PB-10).

### [MEDIUM] AP-12 Tratamento de erros por except puro
File: routes/task_routes.py:62, routes/task_routes.py:136-138, routes/task_routes.py:204-205, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221, utils/helpers.py:46-50, utils/helpers.py:88
Description: `except:` puro engolindo qualquer erro (inclusive KeyboardInterrupt) e devolvendo mensagens genéricas; try/except repetido em cada rota; nenhum error handler global.
Impact: Bugs mascarados, sem log da causa.
Recommendation: Exceções de domínio + errorhandler global com log (PB-10).

### [MEDIUM] AP-15 Deprecated API
File: routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155; routes/report_routes.py:105, 192, 213; models/task.py:15-16, 52; models/user.py:14; models/category.py:11; utils/helpers.py:38; services/notification_service.py:35; routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172; routes/report_routes.py:35, 42, 45, 71, 133; seed.py:66-74
Description: `Model.query.get(id)` é a API legada do SQLAlchemy 2.x e `datetime.utcnow()` está deprecated desde o Python 3.12.
Impact: DeprecationWarning hoje e remoção em versões futuras.
Recommendation: `db.session.get(Model, id)` e `datetime.now(timezone.utc)` via helper único (PB-12).

### [MEDIUM] AP-14 Exclusão em cascata silenciosa
File: routes/user_routes.py:140-151
Description: DELETE /users/<id> apaga todas as tasks do usuário no handler, sem cascade declarado no model nem aviso ao cliente.
Impact: Perda de dados silenciosa, regra escondida na rota.
Recommendation: cascade no relacionamento do model ou service explícito, na mesma transação (PB-15).

### [LOW] AP-18 Imports não usados e código morto
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:5-6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:2-7, utils/helpers.py:9-55, requirements.txt:4-6
Description: Imports de os/sys/json/hashlib/time sem uso; funções nunca chamadas (format_date, calculate_percentage importadas sem uso, validate_email, sanitize_string, generate_id, log_action, is_valid_color); dependências marshmallow, requests e python-dotenv declaradas mas não usadas; `type(tags) == list` em vez de isinstance.
Impact: Ruído e superfície de manutenção sem benefício.
Recommendation: Remover o que não é usado (PB-16).

### [LOW] AP-16 Magic numbers e constantes duplicadas
File: routes/task_routes.py:110, routes/task_routes.py:177, routes/user_routes.py:71, routes/user_routes.py:120, routes/user_routes.py:64, routes/user_routes.py:115, routes/report_routes.py:45, utils/helpers.py:110-116
Description: Listas de status/roles, tamanho mínimo de senha (4) e janela de 7 dias repetidos como literais, enquanto utils/helpers.py define constantes equivalentes que ninguém usa; p1..p5 desenrolados um a um.
Impact: Valores de negócio duplicados e propensos a divergir.
Recommendation: Constantes únicas em config/constants (PB-13).

### [LOW] AP-17 print como log
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21-24
Description: print() usado como log de eventos e de erros.
Impact: Sem níveis nem controle de saída.
Recommendation: logging (PB-14).

### [LOW] AP-18 Estilo verboso
File: models/task.py:38-60, models/user.py:34-38, routes/task_routes.py:30-39
Description: `if cond: return True else: return False` e ifs aninhados em vez de retorno direto de expressão.
Impact: Leitura mais difícil.
Recommendation: Simplificar as expressões (PB-16).

================================
Total: 17 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
