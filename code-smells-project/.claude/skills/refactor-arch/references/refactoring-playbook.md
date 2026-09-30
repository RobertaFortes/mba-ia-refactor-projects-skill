# Playbook de Refatoração (Fase 3)

Padrões de transformação **antes → depois**. Os exemplos usam Python e JavaScript; aplique o mesmo princípio em outras linguagens. Cada padrão indica os anti-patterns (`AP-xx`) que resolve.

| Padrão | Resolve | Resumo |
|---|---|---|
| PB-01 Extrair configuração e segredos | AP-01, AP-16 | Ler de variáveis de ambiente em módulo `config` |
| PB-02 Parametrizar queries | AP-02 | Placeholders em vez de concatenação |
| PB-03 Quebrar o God File em camadas MVC | AP-03 | Models / Controllers / Routes / entry point |
| PB-04 Mover regra de negócio para fora do controller | AP-06 | Controller orquestra; model/service decide |
| PB-05 Eliminar estado global (DI + factory) | AP-07 | Dependências criadas no entry point e injetadas |
| PB-06 Hash seguro de senha e autenticação | AP-05 | Hash salgado + verificação; nada de token falso |
| PB-07 Serializer sem dados sensíveis | AP-08, AP-13 | `to_dict()` central que omite senha/segredos |
| PB-08 Proteger ou remover endpoints perigosos | AP-04 | Sem SQL arbitrário; admin só com token/flag |
| PB-09 Eliminar N+1 | AP-10 | JOIN / eager loading / `IN` |
| PB-10 Validação e erros centralizados | AP-11, AP-12 | Validators reutilizáveis + error handler global |
| PB-11 Callbacks → async/await | AP-09 | Promises, `Promise.all`, sem contadores manuais |
| PB-12 Substituir APIs deprecated | AP-15 | Trocar pelo equivalente moderno |
| PB-13 Constantes nomeadas | AP-16 | Sem magic numbers/strings |
| PB-14 Logging estruturado | AP-17 | Logger em vez de `print`/`console.log`; sem dados sensíveis |
| PB-15 Transações e integridade | AP-14 | Operação multi-etapa atômica; cascade |
| PB-16 Limpeza de legibilidade | AP-18 | Nomes claros, remover imports/código morto |

---

## PB-01 — Extrair configuração e segredos
**Antes**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
```js
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };
```
**Depois**
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    PORT = int(os.environ.get("PORT", 5000))
```
```js
// src/config/settings.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  dbPath: process.env.DB_PATH || ':memory:',
};
```
Crie `.env.example` com os nomes (sem valores reais). Nunca imprima segredos em logs/respostas. Defaults só para desenvolvimento, nunca chaves "live".

## PB-02 — Parametrizar queries
**Antes**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```
**Depois**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
# busca dinâmica: monte a lista de condições e a lista de parâmetros em paralelo
sql, params = "SELECT * FROM produtos WHERE 1=1", []
if termo:
    sql += " AND (nome LIKE ? OR descricao LIKE ?)"
    params += [f"%{termo}%"] * 2
cursor.execute(sql, params)
```
Nomes de colunas/tabelas que vêm do usuário nunca são interpolados: use *allowlist*.

## PB-03 — Quebrar o God File em camadas MVC
**Antes:** um arquivo/classe com rotas + SQL + schema + regras.
```js
class AppManager {
  initDb() {/* CREATE TABLE ... */}
  setupRoutes(app) { app.post('/api/checkout', (req, res) => { /* validação + SQL + pagamento + auditoria */ }); }
}
```
**Depois:** um arquivo por responsabilidade.
```
src/config/settings.js
src/models/database.js        # conexão + initSchema/seed
src/models/courseModel.js     # findActiveById
src/models/userModel.js       # findByEmail, create, remove
src/models/enrollmentModel.js
src/models/paymentModel.js
src/services/paymentService.js
src/controllers/checkoutController.js   # orquestra o caso de uso
src/routes/checkoutRoutes.js            # POST /api/checkout -> controller
src/middlewares/errorHandler.js
src/app.js                               # composition root
```
Passos: (1) inventarie responsabilidades do arquivo; (2) crie os módulos vazios; (3) mova o código por responsabilidade, mantendo assinaturas; (4) reduza o arquivo original ao entry point ou apague-o; (5) rode o baseline.

## PB-04 — Mover regra de negócio para fora do controller
**Antes** (dentro do handler)
```python
total = 0
for item in itens:
    produto = cursor.execute("SELECT * FROM produtos WHERE id = ...").fetchone()
    if produto["estoque"] < item["quantidade"]: return {"erro": "Estoque insuficiente"}
    total += produto["preco"] * item["quantidade"]
print("ENVIANDO EMAIL ...")
```
**Depois**
```python
# controllers/pedido_controller.py — orquestra
def criar_pedido():
    dados = validar_pedido(request.get_json())            # PB-10
    resultado = pedido_service.criar(dados["usuario_id"], dados["itens"])
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

# services/pedido_service.py — decide
def criar(usuario_id, itens):
    total = calcular_total(itens)                          # regra
    pedido_id = pedido_model.criar_com_itens(usuario_id, itens, total)  # PB-15
    notificacao_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}
```
Regra prática: se o trecho não depende de `request`/`response`, ele não pertence ao controller.

## PB-05 — Eliminar estado global (DI + factory)
**Antes**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None: db_connection = sqlite3.connect(...)
    return db_connection
```
```js
let globalCache = {}; let totalRevenue = 0;   // mutados por várias funções
```
**Depois**
```python
# app.py
def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    init_db(settings.DATABASE_PATH)          # models/database.py: get_connection() por request/contexto
    register_routes(app)
    register_error_handlers(app)
    return app
```
```js
// services/cacheService.js — estado encapsulado e injetável
class CacheService { #store = new Map(); set(k, v){ this.#store.set(k, v); } get(k){ return this.#store.get(k); } }
module.exports = CacheService;   // instanciado no app.js e passado ao controller
```
Variáveis mortas (`totalRevenue`) são removidas. Conexões: uma por request/contexto (`flask.g`, pool) ou instância criada no entry point e injetada — nunca `global`.

## PB-06 — Hash seguro de senha e autenticação
**Antes**
```python
cursor.execute("INSERT INTO usuarios ... VALUES ('" + nome + "', '" + email + "', '" + senha + "')")   # texto puro
self.password = hashlib.md5(pwd.encode()).hexdigest()
return {'token': 'fake-jwt-token-' + str(user.id)}
```
```js
function badCrypto(pwd){ /* base64 em loop */ }
```
**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash   # já vem com Flask
senha_hash = generate_password_hash(senha)
ok = check_password_hash(row["senha"], senha)
```
```js
const crypto = require('crypto');
const hashPassword = (pwd) => { const salt = crypto.randomBytes(16).toString('hex');
  return `${salt}:${crypto.scryptSync(pwd, salt, 64).toString('hex')}`; };
const verifyPassword = (pwd, stored) => { const [salt, key] = stored.split(':');
  return crypto.timingSafeEqual(Buffer.from(key, 'hex'), crypto.scryptSync(pwd, salt, 64)); };
```
Seeds/usuários de exemplo passam a ser criados já com hash. Se o login precisava aceitar senhas antigas em texto puro, faça migração no boot (rehash ao logar). O "token falso" deve ser mantido apenas se fizer parte do contrato; registre como *Behavior change* se substituído por token assinado (ex.: `itsdangerous`/JWT).

## PB-07 — Serializer sem dados sensíveis (e sem duplicação)
**Antes**
```python
result.append({"id": row["id"], "nome": row["nome"], "email": row["email"], "senha": row["senha"], ...})  # repetido 3x
```
```python
def to_dict(self): return {'id': self.id, 'email': self.email, 'password': self.password, ...}
```
**Depois**
```python
# models/usuario_model.py
PUBLIC_FIELDS = ("id", "nome", "email", "tipo", "criado_em")
def to_public_dict(row): return {k: row[k] for k in PUBLIC_FIELDS}
```
Um único serializer por entidade, usado por todas as rotas. Campo removido da resposta = *Behavior change* a registrar.

## PB-08 — Proteger ou remover endpoints perigosos
**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query(): cursor.execute(request.get_json()["sql"])   # SQL arbitrário, sem auth
@app.route("/admin/reset-db", methods=["POST"])
def reset_database(): ...DELETE FROM ...
# health devolve secret_key, db_path, debug
```
**Depois**
```python
# middlewares/auth.py
def require_admin(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not Settings.ADMIN_TOKEN or request.headers.get("X-Admin-Token") != Settings.ADMIN_TOKEN:
            return jsonify({"erro": "Acesso negado", "sucesso": False}), 403
        return fn(*a, **kw)
    return wrapper
```
- `/admin/query` (SQL arbitrário): **remova** (ou restrinja a consultas pré-definidas). Se a rota precisar continuar respondendo, ela responde `403/404` com mensagem clara — registre como *Behavior change*.
- Rotas destrutivas (`reset-db`): mantenha somente atrás de `require_admin` **e** flag de ambiente (`ENABLE_ADMIN_ENDPOINTS=true`).
- `health`: devolva apenas `status`/contagens; nunca segredos, caminhos ou flags de debug.
- `DEBUG` vem de config (`false` por padrão).

## PB-09 — Eliminar N+1
**Antes**
```python
for pedido in pedidos:
    itens = cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(pedido["id"]))
    for item in itens:
        prod = cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
```python
for t in tasks:  user = User.query.get(t.user_id); cat = Category.query.get(t.category_id)
```
**Depois**
```python
# uma query com JOIN e agrupamento em memória
rows = cursor.execute("""
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?""", (usuario_id,)).fetchall()
```
```python
# ORM: eager loading
Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
# contagem por grupo em 1 query
db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
```
Preserve o formato final do JSON (ex.: `"Desconhecido"` quando o produto não existe → `COALESCE(pr.nome, 'Desconhecido')`).

## PB-10 — Validação e tratamento de erros centralizados
**Antes:** cada handler com `try/except Exception as e: return jsonify({"erro": str(e)}), 500` e `if "nome" not in dados` repetido.
**Depois**
```python
# middlewares/error_handler.py
class AppError(Exception):
    status = 500
    def __init__(self, message, status=None): super().__init__(message); self.status = status or self.status
class ValidationError(AppError): status = 400
class NotFoundError(AppError): status = 404

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e): return jsonify({"erro": str(e), "sucesso": False}), e.status
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```
```js
// src/middlewares/errorHandler.js (registrado por último)
module.exports = (err, req, res, next) => {
  const status = err.status || 500;
  if (status >= 500) console.error(err);
  res.status(status).json({ error: status >= 500 ? 'Erro interno' : err.message });
};
```
Validators (`validar_produto(dados)`) ficam em `utils/validators` ou no model e são usados por POST **e** PUT. Mantenha as mesmas mensagens/códigos de erro do original quando possível. Nunca devolva `str(e)` de exceções inesperadas.

## PB-11 — Callbacks → async/await (Node)
**Antes**
```js
this.db.get(sql, [cid], (err, course) => {
  this.db.get(sql2, [e], (err, user) => {
    this.db.run(sql3, [...], function (err) { ... this.lastID ... });
```
**Depois**
```js
// models/database.js — helpers com Promises
const run = (db, sql, p = []) => new Promise((ok, ko) => db.run(sql, p, function (e) { e ? ko(e) : ok({ lastID: this.lastID, changes: this.changes }); }));
const get = (db, sql, p = []) => new Promise((ok, ko) => db.get(sql, p, (e, r) => e ? ko(e) : ok(r)));
const all = (db, sql, p = []) => new Promise((ok, ko) => db.all(sql, p, (e, r) => e ? ko(e) : ok(r)));

// controller
async function checkout(req, res, next) {
  try {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new NotFoundError('Curso não encontrado');
    ...
    res.status(200).json({ msg: 'Sucesso', enrollment_id });
  } catch (err) { next(err); }
}
```
Substitua contadores manuais (`pending--`) por `await Promise.all(items.map(...))`. Exija try/catch + `next(err)` (ou wrapper `asyncHandler`) em todo handler async.

## PB-12 — Substituir APIs deprecated
| Antes | Depois |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` (para colunas naive do SQLite: `.replace(tzinfo=None)` ou helper `utcnow()` central) |
| `Model.query.get(id)` | `db.session.get(Model, id)` |
| `new Buffer(str)` | `Buffer.from(str)` |
| `var x` | `const` / `let` |
| `app.run(debug=True)` fixo | `app.run(debug=settings.DEBUG)` |
| `ioutil.ReadAll` (Go) | `io.ReadAll` |

**Antes → depois (SQLAlchemy)**
```python
user = User.query.get(t.user_id)
user = db.session.get(User, t.user_id)
created_at = db.Column(db.DateTime, default=datetime.utcnow)
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```
Crie um helper único (`utils/time.py: utcnow()`) para não espalhar a conversão. Confira o comportamento após a troca (comparações naive vs aware).

## PB-13 — Constantes nomeadas
**Antes**
```python
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
```
**Depois**
```python
# config/constants.py
DESCONTO_FAIXAS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))   # (faturamento mínimo, taxa)
STATUS_PEDIDO_VALIDOS = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
```
Valores de negócio duplicados (listas de status, roles, tamanhos mínimos) ficam em **uma** definição só.

## PB-14 — Logging adequado
**Antes**
```python
print("ENVIANDO EMAIL: Pedido " + str(id)); print(f"Processando cartão {cc} ...")
```
**Depois**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Pedido %s criado para usuário %s", pedido_id, usuario_id)
```
```js
console.log(`[checkout] cartão ****${card.slice(-4)}`);   // ou logger (pino/winston) se já existir no projeto
```
Nunca logue número completo de cartão, senha, token ou chave. Notificações simuladas por `print` viram chamadas a um `notification_service` (mesmo que apenas faça log).

## PB-15 — Transações e integridade
**Antes**
```python
cursor.execute("INSERT INTO pedidos ...")
for item in itens:
    cursor.execute("INSERT INTO itens_pedido ..."); cursor.execute("UPDATE produtos SET estoque = estoque - ...")
db.commit()      # sem rollback em caso de falha
```
```js
db.run("DELETE FROM users WHERE id = ?", [id]);   // matrículas e pagamentos órfãos
```
**Depois**
```python
try:
    cursor.execute("BEGIN")
    ...  # todas as escritas
    db.commit()
except Exception:
    db.rollback(); raise
```
```js
await run(db, 'BEGIN');
try { /* enrollments, payments, audit */ await run(db, 'COMMIT'); } catch (e) { await run(db, 'ROLLBACK'); throw e; }
// exclusão de usuário: remova (ou desative) registros filhos na mesma transação
await run(db, 'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [id]);
await run(db, 'DELETE FROM enrollments WHERE user_id = ?', [id]);
```
ORM: `cascade="all, delete-orphan"` na relationship, ou `session.delete` dos filhos + um único `commit`.

## PB-16 — Limpeza de legibilidade
- Renomeie variáveis de uma letra/abreviações (`u`→`name`, `cid`→`courseId`, `cc`→`cardNumber`), mantendo os **nomes dos campos do contrato externo** (ex.: o corpo JSON `usr`, `eml`, `c_id` continua sendo lido, apenas mapeado para nomes claros).
- Remova imports, funções e constantes não usados (verifique com busca antes de apagar).
- Simplifique `if cond: return True else: return False` → `return cond`; `type(x) == list` → `isinstance(x, list)`; `except:` → `except Exception:` com tratamento.
- Consolide lógica repetida em um método do model (ex.: `Task.is_overdue()` usado por todas as rotas).

---

## Ordem e cuidados de aplicação

1. Comece por PB-01 e PB-02 (segurança), depois a reestruturação (PB-03/04/05), depois PB-06 a PB-11, por fim PB-12 a PB-16.
2. Após cada bloco grande, suba a aplicação e rode o baseline — falhas são mais fáceis de localizar.
3. Toda mudança de contrato (campo removido, rota desabilitada, hash de senhas) vai para "Behavior changes".
4. Preserve dados de seed/exemplo necessários para o funcionamento (ex.: usuários de teste), agora com senha em hash.
