"""Constantes de negócio (antes espalhadas como magic numbers/strings)."""

CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"

STATUS_PEDIDO_VALIDOS = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
STATUS_PEDIDO_INICIAL = "pendente"
STATUS_PEDIDO_CANCELADO = "cancelado"

TIPO_USUARIO_PADRAO = "cliente"

NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# (faturamento mínimo, taxa de desconto) da maior faixa para a menor
DESCONTO_FAIXAS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
