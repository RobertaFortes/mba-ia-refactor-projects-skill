import logging

from flask import current_app, jsonify

from models import database, pedido_model, produto_model, usuario_model

logger = logging.getLogger(__name__)


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": current_app.config["APP_VERSION"],
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    try:
        counts = {
            "produtos": produto_model.contar(),
            "usuarios": usuario_model.contar(),
            "pedidos": pedido_model.contar(),
        }
    except Exception:
        logger.exception("Falha no health check")
        return jsonify({"status": "erro", "detalhes": "Banco de dados indisponível"}), 500

    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": current_app.config["APP_VERSION"],
        "ambiente": current_app.config["APP_ENV"],
    }), 200


def reset_database():
    database.limpar_dados()
    logger.warning("Banco de dados resetado via endpoint administrativo")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
