import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes import register_routes


def create_app(settings=Settings):
    """Composition root: configuração, extensões, rotas e tratamento de erros."""
    app = Flask(__name__)
    app.config.from_object(settings)

    CORS(app)
    db.init_app(app)

    import models  # noqa: F401  (registra os models no metadata antes do create_all)

    register_routes(app)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    create_app().run(debug=Settings.DEBUG, host=Settings.HOST, port=Settings.PORT)
