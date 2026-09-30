from config.constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)
from utils.errors import ValidationError


def _e_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def validar_produto(dados):
    """Valida o corpo de criação/atualização de produto (mesmas regras para POST e PUT)."""
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"), ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome, preco, estoque = dados["nome"], dados["preco"], dados["estoque"]
    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if not _e_numero(preco):
        raise ValidationError("Preço inválido")
    if not _e_numero(estoque):
        raise ValidationError("Estoque inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")

    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))

    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_usuario(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    dados = dados or {}
    email, senha = dados.get("email", ""), dados.get("senha", "")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    return email, senha


def validar_pedido(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or not isinstance(itens, list):
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("produto_id"), int)
            or not isinstance(item.get("quantidade"), int)
            or item["quantidade"] <= 0
        ):
            raise ValidationError("Item inválido: informe produto_id e quantidade positiva")
    return usuario_id, itens


def validar_status_pedido(dados):
    status = (dados or {}).get("status", "")
    if status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return status


def parse_preco(valor, nome_campo):
    if valor in (None, ""):
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"{nome_campo} inválido")
