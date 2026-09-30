from config.constants import STATUS_PEDIDO_CANCELADO
from models import pedido_model, produto_model
from services import notificacao_service
from utils.errors import ValidationError


def criar_pedido(usuario_id, itens):
    """Valida produtos/estoque, calcula o total e persiste o pedido de forma atômica."""
    total = 0
    itens_resolvidos = []
    for item in itens:
        produto = produto_model.buscar_por_id(item["produto_id"])
        if produto is None:
            raise ValidationError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
        total += produto["preco"] * item["quantidade"]
        itens_resolvidos.append(
            {
                "produto_id": produto["id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"],
            }
        )

    pedido_id = pedido_model.criar_com_itens(usuario_id, itens_resolvidos, total)
    notificacao_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    status_atual = pedido_model.buscar_status(pedido_id)
    devolver_estoque = (
        novo_status == STATUS_PEDIDO_CANCELADO
        and status_atual is not None
        and status_atual != STATUS_PEDIDO_CANCELADO
    )
    pedido_model.atualizar_status(pedido_id, novo_status, devolver_estoque)
    notificacao_service.status_pedido_alterado(pedido_id, novo_status)
