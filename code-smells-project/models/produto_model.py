from models.database import get_db

COLUNAS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def to_dict(row):
    return {coluna: row[coluna] for coluna in COLUNAS}


def listar():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [to_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return to_dict(row) if row else None


def buscar(termo="", categoria=None, preco_min=None, preco_max=None):
    sql, params = "SELECT * FROM produtos WHERE 1=1", []
    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if preco_min:
        sql += " AND preco >= ?"
        params.append(preco_min)
    if preco_max:
        sql += " AND preco <= ?"
        params.append(preco_max)
    return [to_dict(row) for row in get_db().execute(sql, params).fetchall()]


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def remover(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def contar():
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
