from config.constants import TIPO_USUARIO_PADRAO
from models.database import get_db

# Campos que podem sair na API: a senha (hash) nunca é exposta.
CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")


def to_public_dict(row):
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS}


def listar():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [to_public_dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return to_public_dict(row) if row else None


def buscar_credenciais_por_email(email):
    """Retorna a linha completa (inclui hash) — uso exclusivo da autenticação."""
    return get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def criar(nome, email, senha_hash, tipo=TIPO_USUARIO_PADRAO):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_senha(usuario_id, senha_hash):
    db = get_db()
    db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))
    db.commit()


def contar():
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
