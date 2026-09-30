import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: pedido %s criado para usuário %s", pedido_id, usuario_id)
    logger.info("SMS: seu pedido foi recebido")
    logger.info("PUSH: novo pedido recebido pelo sistema")


def status_pedido_alterado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("NOTIFICAÇÃO: pedido %s aprovado, preparar envio", pedido_id)
    elif novo_status == "cancelado":
        logger.info("NOTIFICAÇÃO: pedido %s cancelado, estoque devolvido", pedido_id)
