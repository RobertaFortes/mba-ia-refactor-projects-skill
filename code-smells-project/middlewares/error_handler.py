import logging

from flask import jsonify

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": str(error), "sucesso": False}), error.status

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
