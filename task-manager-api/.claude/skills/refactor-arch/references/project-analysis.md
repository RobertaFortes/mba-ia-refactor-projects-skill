# Heurísticas de Análise de Projeto (Fase 1)

Objetivo: descobrir **linguagem, framework, banco, domínio e arquitetura atual** lendo o código — sem executar nada e sem supor a stack de antemão.

## 1. Listar os arquivos-fonte

Ignore sempre: `.git/`, `.claude/`, `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `target/`, `vendor/`, lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`), bancos (`*.db`, `*.sqlite`), binários e imagens.

"Arquivos-fonte" = arquivos de código da linguagem detectada (`.py`, `.js/.ts`, `.java`, `.go`, `.rb`, `.php`, `.cs`...). Contabilize arquivos e linhas (`wc -l`). Arquivos de config/README não contam como fonte, mas devem ser lidos.

## 2. Detectar a linguagem

Procure primeiro o **manifesto de dependências** na raiz (e em subpastas de primeiro nível):

| Manifesto | Linguagem / ecossistema |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python |
| `package.json` (+ `tsconfig.json` ⇒ TypeScript) | JavaScript / TypeScript (Node.js) |
| `pom.xml`, `build.gradle(.kts)` | Java / Kotlin |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj`, `*.sln` | C# / .NET |
| `Cargo.toml` | Rust |

Confirme pela extensão predominante dos arquivos-fonte. Se houver mais de uma linguagem, reporte a principal (backend) e cite as demais.

## 3. Detectar o framework (e a versão)

Leia as dependências declaradas (com versão) e confirme nos imports do entry point:

| Sinal (dependência / import) | Framework |
|---|---|
| `flask` / `from flask import` | Flask |
| `fastapi` / `from fastapi import` | FastAPI |
| `django` / `INSTALLED_APPS` | Django |
| `express` / `require('express')` / `import express` | Express |
| `@nestjs/core` | NestJS |
| `koa`, `fastify`, `hapi` | Koa / Fastify / Hapi |
| `spring-boot-starter-web`, `@RestController` | Spring Boot |
| `gin-gonic/gin`, `gorilla/mux`, `net/http` | Go (Gin / Mux / stdlib) |
| `rails`, `sinatra` | Rails / Sinatra |
| `laravel/framework` | Laravel |

Inclua extensões relevantes na linha "Dependencies" (ORM, CORS, cliente de banco, etc.). Se a versão não estiver fixada, escreva a faixa declarada (ex.: `^4.18.2`).

## 4. Detectar o banco de dados e as tabelas/entidades

Sinais de banco: imports/dependências `sqlite3`, `psycopg2`, `mysql`, `pg`, `mongoose`, `sqlalchemy`, `flask_sqlalchemy`, `sequelize`, `typeorm`, `prisma`, `gorm`, `hibernate`.

- **SQL cru:** procure `CREATE TABLE` — cada ocorrência é uma tabela.
- **ORM:** procure classes de modelo (`db.Model`, `@Entity`, `Schema`, `sequelize.define`) e seus `__tablename__`/nomes de coleção.
- Anote também: banco em memória (`:memory:`), arquivo local (`*.db`), URL de conexão, seeds de dados.

## 5. Descobrir o domínio

Deduza pelos **nomes de tabelas, rotas, classes e campos**, não pelo nome da pasta. Descreva em uma linha ("E-commerce API (produtos, pedidos, usuários)", "LMS API com fluxo de checkout", "Task Manager API"). Se for ambíguo, cite os substantivos mais frequentes.

## 6. Mapear a arquitetura atual

1. **Entry point:** arquivo que inicializa o servidor (`app.run`, `app.listen`, `main()`, `@SpringBootApplication`). Leia-o inteiro.
2. **Camadas existentes:** identifique pastas/arquivos por responsabilidade:
   - roteamento / mapeamento de URLs (`routes`, `router`, `urls`, `@app.route`, `app.get`);
   - controle do fluxo (`controllers`, handlers);
   - regra de negócio (`services`, `use cases`);
   - acesso a dados / entidades (`models`, `repositories`, `dao`, chamadas SQL);
   - configuração (`config`, `settings`, `.env`);
   - utilitários (`utils`, `helpers`).
3. **Classifique o nível de organização:**
   - *Monolítica / sem camadas:* poucos arquivos misturando rota + regra + SQL (ou um único arquivo/classe fazendo tudo).
   - *Parcialmente em camadas:* existem pastas de camadas, mas com responsabilidades vazando (regra de negócio nas rotas, models anêmicos, `helpers` genérico como depósito).
   - *MVC/camadas adequadas:* separação clara e sem vazamentos.
4. Verifique **quem fala com quem**: rota chama controller? controller chama model? ou rota já chama o banco? Anote inversões de dependência.
5. Verifique **estado global** (variáveis de módulo mutáveis, conexões singleton, caches globais) e **configuração** (valores fixos no código).

## 7. Inventário de rotas

Liste `MÉTODO caminho` de cada endpoint. Onde procurar:

| Stack | Onde estão as rotas |
|---|---|
| Flask | `@app.route`, `@bp.route`, `app.add_url_rule` |
| FastAPI | `@app.get/post/...`, `APIRouter` |
| Django | `urls.py` (`path(...)`) |
| Express/Koa/Fastify | `app.get/post/put/delete`, `router.<verbo>` |
| Spring | `@GetMapping`, `@PostMapping`, `@RequestMapping` |
| Go | `http.HandleFunc`, `r.GET(...)` |

Registre também rotas em loops ou com prefixo de Blueprint/Router (`url_prefix`, `app.use('/api', ...)`). Este inventário é usado para validar a Fase 3.

## 8. Saída

Preencha o bloco `PHASE 1: PROJECT ANALYSIS` do `SKILL.md`. Se algum campo não puder ser determinado, escreva `unknown` — não chute.
