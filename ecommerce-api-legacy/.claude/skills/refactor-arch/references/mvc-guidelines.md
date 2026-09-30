# Guidelines de Arquitetura — MVC alvo (Fase 3)

Este é o padrão para o qual todo projeto é refatorado, independente de linguagem. Em APIs sem HTML renderizado, a **View** é a camada de **rotas + serialização da resposta** (o "o que o cliente vê").

## Camadas e responsabilidades

| Camada | Responsabilidade | PODE | NÃO PODE |
|---|---|---|---|
| **Config** | Ler configuração e segredos do ambiente (`.env`/variáveis), expor constantes | Ter defaults seguros para desenvolvimento | Conter segredos reais hardcoded; ser mutável em runtime |
| **Models** | Representar entidades e **acessar dados** (queries parametrizadas/ORM); regras de domínio que dependem só dos dados; conversão entidade → dict | Conhecer o banco; expor métodos como `find_by_id`, `create`, `to_dict` | Conhecer HTTP (`request`, `res`), formatar resposta, enviar e-mail |
| **Controllers** | Orquestrar o fluxo de um caso de uso: validar entrada, chamar models/serviços, decidir status HTTP e montar o resultado | Chamar vários models, aplicar regra de negócio do caso de uso, chamar serviços (notificação, pagamento) | Conter SQL, conhecer detalhes do banco, registrar rotas |
| **Views / Routes** | Mapear URL + método HTTP → controller; serializar a resposta (JSON) | Aplicar middlewares por rota, definir prefixos/blueprints | Conter regra de negócio ou acesso a dados |
| **Middlewares / Errors** | Tratamento de erros centralizado, autenticação, logging de requisição | Traduzir exceções de domínio em respostas HTTP | Regra de negócio |
| **Entry point (composition root)** | Criar a aplicação, ler config, instanciar dependências, registrar rotas e middlewares, iniciar o servidor | Ser o **único** lugar que "monta" as peças | Conter regra de negócio ou rotas inline |

Camada opcional **Services**: use quando a regra envolver integração externa ou vários models (pagamento, e-mail, relatórios). Controller chama service; service chama models.

## Regra de dependência

`Routes → Controllers → (Services →) Models → Banco`. Setas só apontam para baixo; camadas de baixo **nunca** importam as de cima. Config é injetada/importada por todos, nunca importa ninguém. Dependências (conexão, serviços) são criadas no entry point e **recebidas** por parâmetro/construtor — sem singletons globais mutáveis.

## Regras gerais

1. Um arquivo = uma responsabilidade (idealmente < 150 linhas). Um model/controller por domínio (produto, usuário, pedido, curso, task...).
2. Configuração e segredos apenas em `config`, lidos de variáveis de ambiente, com `.env.example` documentando.
3. Todo acesso a banco usa queries parametrizadas ou ORM.
4. Erros tratados por um handler central; controllers lançam exceções de domínio (ex.: `NotFoundError`, `ValidationError`) em vez de repetir `try/except` + `jsonify`.
5. Respostas nunca incluem senha/hash/segredos.
6. O comando original de execução do projeto continua funcionando.
7. Não renomeie rotas nem mude formatos de resposta (ver "Regras globais" do `SKILL.md`).

## Estrutura de diretórios por stack

Adapte os nomes ao idioma/convenção do projeto (ex.: `produto_model.py`). Mantenha o entry point onde o comando original o espera.

### Python (Flask / FastAPI)
```
<projeto>/
├── app.py                  # entry point: create_app() + app.run (composition root)
├── config/
│   ├── __init__.py
│   └── settings.py         # lê os.environ; classe/constantes de config
├── models/                 # entidades + acesso a dados
│   ├── __init__.py
│   ├── database.py         # conexão/sessão + criação de schema (init_db)
│   └── <entidade>_model.py
├── controllers/            # orquestração por domínio
│   └── <dominio>_controller.py
├── routes/                 # views: URL -> controller (Blueprints)
│   └── <dominio>_routes.py
├── services/               # (opcional) integrações/regras entre models
├── middlewares/
│   └── error_handler.py    # errorhandlers globais + exceções de domínio
├── utils/                  # helpers puros (sem estado, sem I/O de negócio)
└── requirements.txt
```
Projeto que já usa `routes/` + `models/` (ORM): **mantenha o que está certo**, crie `controllers/` extraindo o corpo dos handlers, mova regra de negócio para models/services, centralize erros e config.

### Node.js (Express / Koa / Fastify)
```
<projeto>/
├── src/
│   ├── app.js              # entry point (composition root): monta e escuta
│   ├── config/
│   │   └── settings.js     # process.env + defaults
│   ├── models/             # entidades + acesso a dados (queries parametrizadas)
│   │   ├── database.js     # conexão + init schema/seed
│   │   └── <entidade>Model.js
│   ├── controllers/
│   │   └── <dominio>Controller.js
│   ├── routes/             # views
│   │   └── <dominio>Routes.js
│   ├── services/           # pagamento, cache, auditoria...
│   ├── middlewares/
│   │   └── errorHandler.js
│   └── utils/
├── package.json
└── (scripts/README/api.http preservados)
```

### Java (Spring Boot)
`controller/` (`@RestController` = routes+controllers finos), `service/`, `repository/` + `model/entity`, `config/`, `exception/` (`@ControllerAdvice`).

### Go
`cmd/<app>/main.go` (composition root), `internal/config`, `internal/models`, `internal/controllers` (handlers), `internal/routes`, `internal/middleware`.

### Outros (Django/Rails/Laravel/.NET)
Respeite o MVC nativo do framework (models/views/controllers ou MVT); aplique as mesmas regras de responsabilidade e o mesmo checklist abaixo.

## Adaptando ao nível de organização atual

- **Monolito sem camadas** (poucos arquivos gigantes): crie todas as camadas, distribua o código por domínio, reduza o arquivo original a entry point.
- **Parcialmente em camadas**: não reescreva o que já está bem. Identifique o que falta (geralmente: controllers, config, handler de erros) e o que vaza (regra nas rotas, models anêmicos ou que expõem senha, helpers-depósito) e corrija apenas isso.
- **Já adequado**: faça apenas as correções pontuais (segurança, deprecated, limpeza).

## Checklist de conformidade (usado na re-auditoria)

- [ ] Existe módulo de config; nenhum segredo hardcoded
- [ ] Models abstraem o acesso a dados; nenhum SQL/ORM fora de models
- [ ] Rotas só mapeiam URL → controller
- [ ] Controllers concentram o fluxo; sem SQL, sem registro de rotas
- [ ] Tratamento de erros centralizado
- [ ] Entry point claro e pequeno
- [ ] Nenhum estado global mutável; dependências injetadas
- [ ] Nenhum dado sensível nas respostas
- [ ] Nenhum endpoint perigoso aberto
- [ ] Sem APIs deprecated
