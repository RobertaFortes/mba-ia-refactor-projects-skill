# refactor-arch — Skill de Refatoração Arquitetural para MVC

Skill do Claude Code (`refactor-arch`) que analisa, audita e refatora qualquer projeto backend para o padrão **MVC**, em 3 fases: **análise** da stack, **auditoria** de anti-patterns (com pausa para confirmação) e **refatoração com validação** (boot + endpoints).

Foi aplicada a 3 projetos legados com problemas de arquitetura, segurança e qualidade:

| # | Projeto | Stack | Relatório | 
|---|---|---|---|
| 1 | `code-smells-project` | Python + Flask (API de E-commerce, sem camadas) | [audit-project-1.md](reports/audit-project-1.md) |
| 2 | `ecommerce-api-legacy` | Node.js + Express (LMS com checkout, God Class) | [audit-project-2.md](reports/audit-project-2.md) |
| 3 | `task-manager-api` | Python + Flask (Task Manager, parcialmente em camadas) | [audit-project-3.md](reports/audit-project-3.md) |

A skill vive em `<projeto>/.claude/skills/refactor-arch/` (cópia idêntica nos 3 projetos):

```
.claude/skills/refactor-arch/
├── SKILL.md                          # as 3 fases, regras globais e formatos de saída
└── references/
    ├── project-analysis.md           # heurísticas de detecção de stack/arquitetura (Fase 1)
    ├── anti-patterns-catalog.md      # 18 anti-patterns + APIs deprecated, com sinais e severidade (Fase 2)
    ├── report-template.md            # formato do relatório de auditoria (Fase 2)
    ├── mvc-guidelines.md             # camadas MVC alvo e estrutura por stack (Fase 3)
    └── refactoring-playbook.md       # 16 padrões de transformação antes/depois (Fase 3)
```

---

## Análise Manual

Antes de escrever a skill, li o código dos 3 projetos e listei os problemas de maior impacto arquitetural. Severidades seguem a escala do desafio (CRITICAL / HIGH / MEDIUM / LOW).

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

| Sev. | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | SQL Injection: todas as queries concatenam entrada do usuário (inclusive o login) | `models.py:28, 48-49, 58-60, 110, 127-128, 280, 291-297` | `' OR '1'='1` derruba a autenticação e permite ler/alterar/apagar qualquer dado |
| CRITICAL | Endpoint `/admin/query` executa SQL arbitrário recebido no corpo e `/admin/reset-db` apaga tudo, sem autenticação | `app.py:47-80` | Qualquer cliente controla o banco |
| CRITICAL | `SECRET_KEY` hardcoded e devolvida no `/health` (junto com `db_path` e `debug`) | `app.py:7`, `controllers.py:289` | Segredo público; a chave não pode ser rotacionada sem deploy |
| CRITICAL | Senhas em texto puro no banco, no seed e na comparação do login | `database.py:75-79`, `models.py:110` | Vazamento do banco expõe todas as senhas |
| CRITICAL | God File: `models.py` mistura SQL, regras (total, estoque, desconto), serialização e 4 domínios | `models.py:1-314` | Impossível testar em isolamento; toda mudança tem raio de impacto total |
| HIGH | Regra de negócio e notificações dentro dos controllers/models | `controllers.py:188-220`, `models.py:133-169` | Lógica presa ao HTTP/SQL, não reutilizável |
| HIGH | Conexão global mutável (`global db_connection`) | `database.py:4-12` | Estado compartilhado entre threads, sem injeção de dependência |
| MEDIUM | N+1: pedidos → itens → produtos em queries aninhadas | `models.py:171-233` | Custo cresce com o volume |
| MEDIUM | Validação inconsistente entre POST e PUT de produto | `controllers.py:24-58` vs `64-93` | Regras divergentes e 500 em entrada inválida |
| MEDIUM | Pedido sem transação; cancelar só imprime "devolver estoque" | `models.py:133-169`, `controllers.py:247-250` | Estoque e pedidos inconsistentes |
| LOW | Magic numbers (faixas de desconto 10000/5000/1000) | `models.py:256-262` | Regra de negócio escondida |
| LOW | `print` como log e "envio" de e-mail/SMS/push | `controllers.py:208-210` | Sem níveis, sem controle |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| Sev. | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | Credenciais de produção no código (`pk_live_...`, senha de banco, SMTP) | `src/utils.js:1-7` | Segredos no repositório |
| CRITICAL | God Class `AppManager`: schema, seed, rotas, SQL, pagamento e auditoria | `src/AppManager.js:4-141` | Nenhuma camada tem responsabilidade única |
| CRITICAL | "Criptografia" caseira (`badCrypto`) e senha padrão `123456` | `src/utils.js:17-23`, `src/AppManager.js:68` | Senhas triviais de recuperar |
| CRITICAL | Relatório financeiro e `DELETE /api/users/:id` sem autenticação | `src/AppManager.js:80, 131` | Qualquer um lê receita e apaga usuários |
| HIGH | Log do número completo do cartão e da chave do gateway | `src/AppManager.js:45` | Vazamento de dado de cartão (PCI) em log |
| HIGH | Regra de checkout dentro do handler da rota, com callbacks aninhados em 5 níveis | `src/AppManager.js:28-78` | Difícil de testar; erros ignorados |
| MEDIUM | N+1 no relatório financeiro (curso → matrícula → usuário → pagamento) | `src/AppManager.js:83-127` | Queries crescem com cursos x matrículas |
| MEDIUM | Usuário é criado antes de o pagamento ser aprovado e o DELETE deixa registros órfãos | `src/AppManager.js:69-72, 131-137` | Dados inconsistentes |
| LOW | Nomes de variáveis ruins (`u`, `e`, `p`, `cid`, `cc`) | `src/AppManager.js:29-33` | Legibilidade |
| LOW | Estado global exportado morto (`totalRevenue`) e `console.log` como log | `src/utils.js:9-15, 25` | Código morto e estado global mutável |

### Projeto 3 — `task-manager-api` (Python/Flask, parcialmente em camadas)

| Sev. | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` e credenciais SMTP hardcoded | `app.py:13`, `services/notification_service.py:9-10` | Segredos no repositório |
| CRITICAL | `debug=True` em `0.0.0.0` | `app.py:34` | O debugger do Werkzeug exposto permite execução remota de código |
| CRITICAL | Senhas com MD5 sem salt, token de login falso e nenhuma autorização (qualquer um cria admin ou deleta usuários) | `models/user.py:29,32`, `routes/user_routes.py:52,71-78,119-122,134-151,210` | Contas forjáveis e escalonamento de privilégio trivial |
| HIGH | O hash da senha sai em `User.to_dict()` e é devolvido em vários endpoints | `models/user.py:16-25` | Vazamento de credenciais |
| HIGH | Sem camada de controllers: rotas com validação, ORM e cálculo de relatórios; CRUD de categorias dentro de `report_routes.py` | `routes/task_routes.py`, `routes/report_routes.py:157-223` | A arquitetura em camadas existe só no papel |
| MEDIUM | Cálculo de "atrasada" copiado em 6 pontos, apesar de `Task.is_overdue()` existir e não ser usado | `routes/task_routes.py:30-39,71-80,283-287` e outros | Regra duplicada e divergente |
| MEDIUM | N+1 (`User.query.get` por task, `len(u.tasks)` por usuário) | `routes/task_routes.py:41-57`, `routes/user_routes.py:22` | Lentidão com volume |
| MEDIUM | APIs deprecated: `Model.query.get()` (16 usos) e `datetime.utcnow()` | `routes/*.py`, `models/*.py` | Warnings hoje, remoção depois |
| MEDIUM | `except:` puro engolindo erros | `routes/task_routes.py:62,236` | Bugs mascarados |
| LOW | Código morto: `NotificationService`, `process_task_data`, funções de `helpers.py` e dependências não usadas | `services/`, `utils/helpers.py`, `requirements.txt` | Ruído e falsa sensação de cobertura |
| LOW | Listas de status/roles e `min=4` repetidos como literais (constantes existem mas ninguém usa) | `routes/task_routes.py:110,177`, `utils/helpers.py:110-116` | Valores de negócio duplicados |

---

## Construção da Skill

### Decisões de design

- **`SKILL.md` é o prompt de orquestração; as referências são o conhecimento.** O `SKILL.md` define *o que fazer em cada fase* e os formatos de saída; cada arquivo de `references/` é lido no momento em que a fase precisa. Isso mantém o prompt principal curto e deixa o conhecimento de domínio editável sem mexer no fluxo.
- **Três fases sequenciais com uma trava explícita.** As Fases 1 e 2 são somente leitura. A Fase 2 termina com `Proceed with refactoring (Phase 3)? [y/n]` e a skill tem ordem de parar ali; nada é escrito antes do `y`.
- **Regras globais anti-alucinação:** todo finding precisa de arquivo e linhas conferidos lendo o arquivo; nada é reportado se não puder ser localizado. Na prática isso pegou um erro meu: o `SECRET_KEY` estava em `app.py:7`, não em `:8`, como eu tinha anotado de memória.
- **Preservar o contrato externo.** Rotas, formatos de resposta e o comando de execução não mudam; qualquer exceção (correção de segurança) vira uma linha em **Behavior changes** no resumo final. Isso evita "refatorar" quebrando o cliente.
- **A validação da Fase 3 é comparativa:** antes de mexer em qualquer arquivo a skill sobe a aplicação, registra status e formato de cada rota (baseline), refatora, e refaz as mesmas chamadas comparando o resultado; depois roda uma re-auditoria com os sinais do catálogo.

### Arquivos de referência (as 5 áreas exigidas)

| Área | Arquivo | Conteúdo |
|---|---|---|
| Análise de projeto | `project-analysis.md` | Detecção de linguagem por manifesto, framework por dependência/import, banco e tabelas, domínio, níveis de organização e inventário de rotas por framework |
| Catálogo de anti-patterns | `anti-patterns-catalog.md` | 18 anti-patterns (AP-01…AP-18), cada um com sinais de detecção por stack e severidade; inclui a tabela de **APIs deprecated** (Python, SQLAlchemy, Flask, Node, Java, Go, PHP) |
| Template de relatório | `report-template.md` | Formato exato do relatório, regras de preenchimento (linhas exatas, ordem CRITICAL→LOW, agrupamento) e exemplo |
| Guidelines de arquitetura | `mvc-guidelines.md` | Responsabilidades de Config, Models, Controllers, Views/Routes, Middlewares e Entry point; regra de dependência; estrutura por stack (Flask/FastAPI, Express, Spring, Go) e como adaptar a projetos já organizados |
| Playbook de refatoração | `refactoring-playbook.md` | 16 padrões (PB-01…PB-16) com exemplos de código antes/depois em Python e JavaScript |

### Anti-patterns do catálogo e por quê

- **CRITICAL:** credenciais hardcoded (AP-01), SQL Injection (AP-02), God Class/File (AP-03), endpoints admin/debug expostos (AP-04), senhas sem hash seguro e autenticação fraca (AP-05). São falhas de segurança ou de separação total de responsabilidades que os 3 projetos têm.
- **HIGH:** regra de negócio no controller (AP-06), estado global e acoplamento sem DI (AP-07), dados sensíveis nas respostas (AP-08), callback hell (AP-09).
- **MEDIUM:** N+1 (AP-10), validação inconsistente (AP-11), erros sem tratamento central (AP-12), duplicação (AP-13), operações sem transação (AP-14) e **APIs deprecated (AP-15)**.
- **LOW:** magic numbers (AP-16), `print`/`console.log` como log (AP-17), legibilidade e código morto (AP-18).

Cada entrada descreve o *sinal acionável* (por exemplo "query SQL dentro de `for`", `execute("..." + var)`, `Model.query.get(`), e não uma categoria vaga como "código ruim".

### Como garanti que a skill é agnóstica de tecnologia

1. Nada no `SKILL.md` cita uma linguagem: ele manda *detectar* a stack via `project-analysis.md`, que tem tabelas por manifesto (`requirements.txt`, `package.json`, `pom.xml`, `go.mod`…) e por framework.
2. Os sinais do catálogo são descritos por comportamento e trazem equivalentes por stack (`execute("…" + x)` em Python, template literal com `${}` em JS; `db.session` / `db.run`).
3. O `mvc-guidelines.md` define as responsabilidades das camadas de forma independente e depois mapeia o layout para cada stack.
4. A prova está na execução: a **mesma cópia da skill**, sem edições, foi aplicada a Flask sem camadas, Express com God Class e Flask parcialmente organizado.
5. A regra "em projeto já organizado, **evolua** a estrutura em vez de recriá-la" cobre o projeto 3.

### Desafios encontrados e como resolvi

- **Ferramenta de execução.** A CLI `claude` do meu terminal estava com o token OAuth revogado (erro 401 ao rodar `claude -p "/refactor-arch"`). As 3 execuções foram feitas dentro do Claude Code (app desktop) invocando a skill `refactor-arch` pelo mecanismo de Skills, seguindo o mesmo `SKILL.md`. Vale rodar `claude "/refactor-arch"` no terminal, após `/login`, para conferir; os relatórios e o código refatorado aqui vêm da execução na sessão do app.
- **Porta 5000 ocupada** (AirPlay do macOS) ao subir o baseline do projeto 1. Solução: subir o app importando-o em outra porta e, na versão refatorada, aceitar `PORT` por variável de ambiente.
- **Processo de teste que sobrevive.** Um servidor da rodada anterior continuou vivo e um teste bateu nele por engano (parecia um bug de autorização). Passei a matar pelo PID e a confirmar que não sobrou processo.
- **Mudar formatos sem quebrar clientes.** Para os 3 projetos foi preciso decidir o que é *bug de segurança* (remover `senha` das respostas) e o que é *contrato* (rotas, códigos de status). O resumo "Behavior changes" registra as poucas exceções.
- **Dados legados.** Bancos antigos têm senhas em texto puro (projeto 1) ou MD5 (projeto 3). Em vez de quebrar o login, o código novo aceita o formato antigo uma vez e migra para hash forte. Testei isso.
- **Severidade consistente.** Ao revisar o relatório do projeto 3 encontrei um finding que eu tinha classificado acima do que o catálogo define; corrigi para seguir a tabela do catálogo.

---

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| 1 — code-smells-project | 5 | 3 | 5 | 3 | **16** |
| 2 — ecommerce-api-legacy | 4 | 4 | 4 | 3 | **15** |
| 3 — task-manager-api | 3 | 4 | 6 | 4 | **17** |

Todos os projetos têm >= 5 findings e pelo menos 1 CRITICAL/HIGH; o projeto 3 (parcialmente organizado) foi auditado por *responsabilidade das camadas*, não só por código: controllers ausentes, models anêmicos e serviços mortos aparecem no relatório.

### Comparação antes/depois

**Projeto 1** — de 4 arquivos planos para MVC:

```
ANTES                     DEPOIS
app.py                    app.py                     (composition root)
controllers.py            config/     settings.py, constants.py
models.py                 models/     database.py, seed.py, produto_/usuario_/pedido_model.py
database.py               controllers/ produto_, usuario_, pedido_, relatorio_, sistema_controller.py
                          routes/     produto_, usuario_, pedido_, relatorio_, sistema_routes.py
                          services/   pedido_, usuario_, relatorio_, notificacao_service.py
                          middlewares/ error_handler.py, auth.py
                          utils/      validators.py, errors.py
```

**Projeto 2** — de God Class para MVC em `src/`:

```
ANTES                     DEPOIS
src/app.js                src/app.js                 (composition root, injeção de dependências)
src/AppManager.js         src/config/     settings.js, constants.js
src/utils.js              src/models/     database.js, schema.js, user/course/enrollment/payment/auditLog/report
                          src/services/   checkout, payment, cache, password, report
                          src/controllers/ checkout, admin
                          src/routes/     checkout, admin
                          src/middlewares/ adminAuth.js, errorHandler.js
                          src/utils/      errors, asyncHandler, logger
```

**Projeto 3** — evolução da estrutura existente:

```
ANTES                                   DEPOIS
app.py                                  app.py                      (create_app)
models/ task, user, category            config/      settings.py, constants.py
routes/ task, user, report(+categories) models/      task, user, category (regras de domínio)
services/ notification_service (morto)  controllers/ task, user, category, report, system
utils/ helpers.py (quase tudo morto)    routes/      task, user, category, report, system
                                        services/    task, user, category, report, auth
                                        middlewares/ auth.py, error_handler.py
                                        utils/       validators.py, errors.py, time.py
```

### Validação

Cada projeto foi validado por comparação com o comportamento original. Scripts e saídas (antes/depois) estão em [`reports/validation/`](reports/validation/).

| Projeto | Boot | Endpoints | Observação |
|---|---|---|---|
| 1 | sem erros | 26/28 chamadas com o mesmo status; as 2 restantes são `/admin/query` (200→404) e `/admin/reset-db` (200→403), fechados de propósito | login com `' OR '1'='1` retorna 401; cancelar pedido devolve o estoque (50→45→50) |
| 2 | sem erros, também via `npm start` | todas as chamadas com o mesmo status e formato; `financial-report` e `DELETE` exigem `X-Admin-Token` (403 sem ele) | cartão recusado não deixa mais usuário órfão |
| 3 | sem erros | 32 chamadas com o mesmo status e formato; **16/16 rotas de leitura com valores idênticos** ao código original sobre o mesmo banco | regras de autorização e migração de hash MD5 testadas (13 verificações) |

### Checklist de validação

**Projeto 1 — code-smells-project**
- [x] Fase 1: linguagem (Python), framework (Flask 3.1.1), domínio (e-commerce) e 4 arquivos analisados
- [x] Fase 2: segue o template; cada finding com arquivo e linhas; ordem CRITICAL → LOW; 16 findings; deprecated verificado (nenhum encontrado); pausa e pede confirmação
- [x] Fase 3: estrutura MVC; config extraída; models; routes; controllers; error handling centralizado; entry point claro; app inicia sem erros; endpoints originais respondem

**Projeto 2 — ecommerce-api-legacy**
- [x] Fase 1: linguagem (JavaScript/Node), framework (Express ^4.18.2), domínio (LMS com checkout) e 3 arquivos analisados
- [x] Fase 2: template; linhas exatas; ordenado; 15 findings; deprecated verificado (nenhum encontrado); pausa e pede confirmação
- [x] Fase 3: estrutura MVC em `src/`; config sem hardcoded; models; routes; controllers; `errorHandler` central; `app.js` como entry point; `npm start` sobe sem erros; endpoints respondem

**Projeto 3 — task-manager-api**
- [x] Fase 1: Python/Flask 3.0.0, domínio Task Manager, 13 arquivos analisados
- [x] Fase 2: template; linhas exatas; ordenado; 17 findings incluindo **APIs deprecated** (`Query.get`, `datetime.utcnow`); pausa e pede confirmação
- [x] Fase 3: controllers criados sobre a estrutura existente; config extraída; `create_app`; error handler global; app inicia; endpoints respondem

### Observações sobre o comportamento em stacks diferentes

- **Flask sem camadas (projeto 1):** a skill precisou criar todas as camadas e redistribuir o código por domínio; o SQL cru foi parametrizado.
- **Express (projeto 2):** o ponto mais delicado foi o assíncrono (callbacks → `async/await` com `Promise`s sobre o `sqlite3`) e serializar transações numa conexão única. A validação comparativa continuou funcionando porque compara HTTP, não código.
- **Flask parcialmente organizado (projeto 3):** a skill *evoluiu* a estrutura (adicionou controllers, config e middlewares, moveu categorias para fora de `report_routes.py`, apagou o código morto) e resolveu N+1 com `joinedload` e `GROUP BY`.
- **Limitação honesta:** a validação prova equivalência das rotas exercitadas pelos smoke tests, não cobertura total. E a re-auditoria da Fase 3 é feita por busca de sinais no código novo, não por análise estática formal.

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude` no terminal; use `/login` se o token tiver expirado)
- Python 3.10+ (projetos 1 e 3) e Node.js 18+ (projeto 2)

### Executar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill imprime a Fase 1, o relatório da Fase 2 e pergunta `Proceed with refactoring (Phase 3)? [y/n]`. Responda `y` para refatorar. Para reexecutar do zero sobre o código original, use uma cópia do commit `ebf62a5` (projetos originais, antes da skill e da refatoração): `git worktree add ../original ebf62a5`; depois copie a pasta `.claude/skills/refactor-arch/` para dentro do projeto que quiser refatorar.

### Rodar os projetos refatorados

```bash
# Projeto 1 (porta configurável por PORT)
cd code-smells-project && pip install -r requirements.txt && PORT=5055 python app.py

# Projeto 2 (endpoints admin exigem ADMIN_TOKEN)
cd ecommerce-api-legacy && npm install && ADMIN_TOKEN=um-token npm start

# Projeto 3
cd task-manager-api && pip install -r requirements.txt && python seed.py && python app.py
```

### Validar que a refatoração funcionou

Com a aplicação rodando, execute o script de smoke test do projeto e compare com a saída "antes" registrada:

```bash
python reports/validation/smoke_p1.py http://127.0.0.1:5055   # compare com reports/validation/p1-before.txt
python reports/validation/smoke_p2.py http://127.0.0.1:3000 um-token
python reports/validation/smoke_p3.py http://127.0.0.1:5000
```

As diferenças esperadas são apenas as mudanças de segurança descritas em "Validação" (campos sensíveis removidos das respostas, endpoints administrativos protegidos).
