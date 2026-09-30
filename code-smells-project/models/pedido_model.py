from config.constants import STATUS_PEDIDO_INICIAL
from models.database import get_db
from utils.errors import ValidationError

_SELECT_PEDIDOS = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario,
           CASE WHEN i.id IS NULL THEN NULL ELSE COALESCE(pr.nome, 'Desconhecido') END AS produto_nome,
           i.id AS item_id
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _agrupar(rows):
    """Agrupa as linhas do JOIN em pedidos com a lista de itens (1 query, sem N+1)."""
    pedidos = {}
    for row in rows:
        pedido = pedidos.setdefault(
            row["id"],
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            },
        )
        if row["item_id"] is not None:
            pedido["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(pedidos.values())


def listar_todos():
    rows = get_db().execute(_SELECT_PEDIDOS + " ORDER BY p.id, i.id").fetchall()
    return _agrupar(rows)


def listar_por_usuario(usuario_id):
    rows = get_db().execute(_SELECT_PEDIDOS + " WHERE p.usuario_id = ? ORDER BY p.id, i.id", (usuario_id,)).fetchall()
    return _agrupar(rows)


def buscar_status(pedido_id):
    row = get_db().execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    return row["status"] if row else None


def criar_com_itens(usuario_id, itens, total):
    """Cria pedido, itens e baixa de estoque em uma única transação atômica.

    `itens` é uma lista de dicts com produto_id, quantidade e preco_unitario.
    """
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PEDIDO_INICIAL, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            baixa = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if baixa.rowcount == 0:
                raise ValidationError(f"Estoque insuficiente para o produto {item['produto_id']}")
        db.commit()
        return pedido_id
    except Exception:
        db.rollback()
        raise


def atualizar_status(pedido_id, novo_status, devolver_estoque=False):
    """Atualiza o status; opcionalmente devolve ao estoque os itens do pedido (cancelamento)."""
    db = get_db()
    try:
        db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        if devolver_estoque:
            db.execute(
                """
                UPDATE produtos
                SET estoque = estoque + (SELECT COALESCE(SUM(i.quantidade), 0)
                                         FROM itens_pedido i
                                         WHERE i.pedido_id = ? AND i.produto_id = produtos.id)
                WHERE id IN (SELECT produto_id FROM itens_pedido WHERE pedido_id = ?)
                """,
                (pedido_id, pedido_id),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise


def resumo_vendas():
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """
    ).fetchone()
    return dict(row)


def contar():
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
