import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from models.database import close_db, init_db
from routes import register_routes


def create_app(settings=Settings):
    """Composition root: monta configuração, banco, rotas e tratamento de erros."""
    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app)

    init_db(app.config["DATABASE_PATH"])
    app.teardown_appcontext(close_db)
    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger(__name__).info("Servidor iniciado em http://localhost:%s", Settings.PORT)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
