# Catálogo de Anti-Patterns (Fase 2)

Cada entrada traz: **severidade**, **sinais de detecção** (o que procurar no código, por stack) e **por que importa**. Use os IDs (`AP-xx`) nos findings.

## Escala de severidade

| Severidade | Critério |
|---|---|
| **CRITICAL** | Falhas graves de arquitetura ou segurança: expõem dados sensíveis, permitem execução/injeção, credenciais hardcoded, ou violam por completo a separação de responsabilidades ("God Class"). |
| **HIGH** | Fortes violações de MVC/SOLID que travam manutenção e testes: regra de negócio nos controllers/rotas, acoplamento forte sem injeção de dependência, estado global mutável. |
| **MEDIUM** | Padronização, duplicação, performance moderada: N+1, validação ausente/duplicada, tratamento de erro inadequado, APIs deprecated. |
| **LOW** | Legibilidade: nomes ruins, magic numbers, logs com `print`/`console.log`, imports não usados. |

Regra de decisão: quando um problema encaixa em duas severidades, use a **maior** se houver exposição de dados/execução de código; senão a menor.

---

## CRITICAL

### AP-01 — Credenciais e segredos hardcoded  `CRITICAL`
Senhas, chaves de API, tokens, `SECRET_KEY`, chaves de gateway de pagamento, usuário/senha SMTP ou de banco escritos no código.
**Sinais:** atribuição literal a nomes contendo `secret`, `password`, `pass`, `pwd`, `token`, `api_key`, `apikey`, `key`, `smtp`, `dbUser`; prefixos de chaves (`pk_live_`, `sk_`, `AKIA`); `app.config['SECRET_KEY'] = '...'`; objeto `config = {...}` com segredos; `.env` versionado.
**Impacto:** vazamento por repositório/logs; impossível rotacionar sem novo deploy.

### AP-02 — SQL Injection (SQL montado por concatenação)  `CRITICAL`
**Sinais:** `execute("... " + var)`, f-strings/`%`/`.format()` dentro de SQL, template literals com `${}` em query, `LIKE '%" + termo + "%'`, ausência de placeholders (`?`, `%s`, `:nome`, `$1`) em queries com entrada do usuário.
**Impacto:** leitura/alteração arbitrária do banco (ex.: `' OR '1'='1` no login).

### AP-03 — God Class / God File (sem separação de camadas)  `CRITICAL`
Um arquivo ou classe concentrando roteamento + regra de negócio + acesso a dados + inicialização/schema do banco + formatação de resposta.
**Sinais:** classe/arquivo com > ~150 linhas que registra rotas **e** faz queries **e** cria tabelas; nome genérico (`AppManager`, `Manager`, `Utils`, `Helper`, `Service` que faz tudo); um `models` que também valida, formata e faz relatórios de vários domínios; rotas definidas dentro de método de classe de dados.
**Impacto:** impossível testar isoladamente; qualquer mudança afeta tudo.

### AP-04 — Endpoints administrativos/debug perigosos expostos  `CRITICAL`
**Sinais:** rota que executa SQL/comando recebido no corpo (`/admin/query`, `eval`, `exec`, `child_process`), rota destrutiva (`/admin/reset-db`, `drop`, `truncate`) **sem autenticação/autorização**; endpoint de health/debug que devolve segredos, caminho do banco, flags de debug; `DEBUG=True` em produção.
**Impacto:** tomada total do sistema por qualquer cliente.

### AP-05 — Senhas sem hash seguro / autenticação fraca  `CRITICAL`
**Sinais:** senha armazenada e comparada em texto puro (`WHERE senha = '...'`, `pass == ...`); MD5/SHA1 sem salt (`hashlib.md5`, `createHash('md5'|'sha1')`); "hash" caseiro (base64 em loop, `badCrypto`); token falso/previsível (`'fake-jwt-token-' + id`); ausência de checagem de autorização em rotas sensíveis.
**Impacto:** vazamento do banco expõe todas as senhas; contas forjáveis.

---

## HIGH

### AP-06 — Regra de negócio no Controller/Rota  `HIGH`
**Sinais:** handlers com cálculos (totais, descontos, taxas), decisões de negócio, efeitos colaterais (envio de e-mail/SMS/push, atualização de estoque) e/ou acesso direto a banco/ORM (`Model.query`, `db.session`, `cursor.execute`, `db.run`) dentro da função da rota; handlers com > ~40 linhas; validação extensa dentro da rota.
**Impacto:** lógica não reutilizável/testável; controller vira God Method.

### AP-07 — Estado global mutável e acoplamento forte / sem injeção de dependência  `HIGH`
**Sinais:** variáveis de módulo mutáveis (`global db_connection`, `let globalCache = {}`, `totalRevenue` alterado por várias funções); singleton de conexão criado por `get_db()` global; `new Dependencia()` instanciado dentro da classe/função em vez de recebido; `import` circular; serviços que criam suas próprias dependências e leem config global.
**Impacto:** testes com estado vazando; impossível trocar implementações.

### AP-08 — Dados sensíveis expostos nas respostas  `HIGH`
**Sinais:** serialização (`to_dict`, `jsonify`, `res.json`) incluindo `password`/`senha`/hash/`token`/`secret_key`; listagens de usuários retornando todas as colunas; `SELECT *` repassado direto ao cliente; stack trace/`str(e)` devolvido ao cliente.
**Impacto:** vazamento de credenciais e detalhes internos.

### AP-09 — Assíncrono mal gerenciado (callback hell / fluxo aninhado)  `HIGH`
Aplica-se a Node/JS (e similares). **Sinais:** callbacks aninhados > 3 níveis; contadores manuais de "pendentes" (`pending--`, `if (pending === 0) res.json`); múltiplos `res.send` possíveis; ausência de `async/await`/Promises; erros de callbacks ignorados (`(err) => { res.send("ok") }`).
**Impacto:** race conditions, respostas duplicadas/perdidas, código ilegível.

---

## MEDIUM

### AP-10 — Queries N+1  `MEDIUM`
**Sinais:** query dentro de `for`/`forEach`/`.map` que busca dados relacionados de cada item (`Model.query.get(x.user_id)` no loop, `SELECT ... WHERE id = ?` por linha, `len(u.tasks)` em loop lazy); cursores aninhados. 
**Correção:** JOIN, `IN (...)`, eager loading (`joinedload`, `include`), agregação no banco.

### AP-11 — Validação ausente, duplicada ou inconsistente  `MEDIUM`
**Sinais:** mesmas regras (`len(title) < 3`, lista de status válidos, regex de e-mail) repetidas em várias rotas/arquivos; validação de tipo ausente (`preco < 0` sem checar se é número; `int(request.args[...])` sem tratamento); PUT com regras diferentes do POST; corpo JSON `None` não tratado (`dados.get` em `None`).
**Impacto:** 500 em entrada inválida; regras divergentes.

### AP-12 — Tratamento de erros inadequado / não centralizado  `MEDIUM`
**Sinais:** `except:` puro ou `except Exception` engolindo erro; `try/except` repetido em cada handler devolvendo `str(e)`; mensagens de erro em formatos diferentes; erros de callback ignorados; ausência de handler global (`@app.errorhandler`, middleware `(err, req, res, next)`).

### AP-13 — Duplicação de código  `MEDIUM`
**Sinais:** blocos idênticos de serialização campo a campo (`{"id": row["id"], ...}` repetido), cálculo de "atrasado/overdue" repetido em várias rotas, funções `get_todos_pedidos` e `get_pedidos_usuario` quase idênticas, helpers definidos mas reimplementados inline.

### AP-14 — Integridade de dados / operações multi-etapa sem transação  `MEDIUM`
**Sinais:** vários `INSERT/UPDATE` relacionados sem transação atômica; exclusão de pai sem tratar filhos (matrículas/pagamentos órfãos, `DELETE` sem cascade); `commit` parcial; estoque decrementado fora de transação.

### AP-15 — Uso de APIs deprecated / obsoletas  `MEDIUM`
Detectar e recomendar o equivalente moderno. Tabela por stack:

| Stack | API obsoleta (sinal) | Equivalente moderno |
|---|---|---|
| Python | `datetime.utcnow()` / `utcfromtimestamp` (deprecated desde 3.12) | `datetime.now(timezone.utc)` |
| Python / SQLAlchemy 2.x | `Model.query.get(id)` (Query API legada) | `db.session.get(Model, id)` |
| Python / SQLAlchemy | `Model.query.filter(...)` legado em projeto novo | `db.session.execute(select(Model)...)` (opcional; reportar como LOW se só estilo) |
| Python / Flask | `app.run(debug=True)` fixo no código; `flask.json.JSONEncoder` customizado; `@app.before_first_request` (removido no 2.3) | debug via variável de ambiente / `flask run --debug`; `app.json.provider`; inicialização no factory |
| Python | `distutils`, `imp`, `asyncio.get_event_loop()` sem loop, `collections.Mapping` | `setuptools`/`packaging`, `importlib`, `asyncio.run`, `collections.abc` |
| Node.js | `new Buffer(x)` / `Buffer()` | `Buffer.from(x)` / `Buffer.alloc(n)` |
| Node.js | `var`; callbacks `err-first` onde há suporte a Promises; `request` (pacote descontinuado); `body-parser` separado (Express ≥ 4.16) | `const/let`; `async/await` + `util.promisify`/driver com Promises; `fetch`/`axios`; `express.json()` |
| Node.js | `fs.exists`, `url.parse`, `crypto.createCipher` | `fs.access`/`fs.promises`, `new URL()`, `crypto.createCipheriv` |
| Node.js / sqlite3 | `db.run/get/all` em cadeia de callbacks | wrapper com Promises (`util.promisify`) ou `sqlite`/`better-sqlite3` |
| Java | `new Date()`, `Calendar`, `Thread.stop`, `Runtime.exec(String)` | `java.time`, ... |
| Go | `ioutil.ReadAll`/`ioutil.ReadFile` | `io.ReadAll`, `os.ReadFile` |
| PHP | `mysql_*`, `each()`, `create_function` | PDO/`mysqli`, `foreach`, closures |

Classificação: MEDIUM quando a API está removida/gera warning em runtime (ex.: `utcnow`, `Query.get`, `new Buffer`), LOW quando é apenas preferência de estilo.

---

## LOW

### AP-16 — Magic numbers e strings  `LOW`
**Sinais:** literais numéricos/strings com significado de negócio soltos no código (`0.1`, `5000`, `10000`, `'pendente'`, `'PAID'`, limites, listas de categorias/status, tamanho mínimo de senha `4`, porta) em vez de constantes nomeadas.

### AP-17 — Logging inadequado (`print` / `console.log` como log)  `LOW`
**Sinais:** `print(...)`/`console.log(...)` para logs de eventos, incluindo dados sensíveis (cartão, senha, email); "notificações" simuladas via print; ausência de níveis de log.
(Se logar **dados sensíveis** como número de cartão completo ou senha, eleve para HIGH.)

### AP-18 — Legibilidade: nomes ruins, imports/código morto  `LOW`
**Sinais:** variáveis de uma letra ou abreviações (`u`, `e`, `p`, `cid`, `cc`, `usr`, `eml`, `pwd`); imports não utilizados (`json`, `sys`, `os`, `hashlib`, `math`, `re`, `time`); funções/constantes definidas e nunca usadas (`generate_id`, `totalRevenue`, `VALID_STATUSES` duplicado); comentários desatualizados; `if x: return True else: return False`; parâmetros/valores de retorno inconsistentes; `type(x) == list` em vez de `isinstance`.

---

## Como reportar

- Um finding por anti-pattern **por arquivo/grupo coeso**, listando todos os locais relevantes (`arquivo:linhas`).
- Sempre ordenar por severidade e depois por número de ocorrências.
- Se um anti-pattern do catálogo **não** existir no projeto, simplesmente não o reporte.
- Se encontrar um problema relevante **fora** do catálogo, reporte-o com a severidade da escala e o ID `AP-XX (fora do catálogo)`.
- Não reportar o mesmo trecho em vários findings sem necessidade: escolha o anti-pattern mais grave que o descreve e cite os demais na descrição.
