import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db
from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': str(error)}), error.status

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, HTTPException):
            return error  # 404/405 etc. mantêm a resposta padrão do Flask
        db.session.rollback()
        logger.exception("Erro não tratado: %s", error)
        return jsonify({'error': 'Erro interno'}), 500
