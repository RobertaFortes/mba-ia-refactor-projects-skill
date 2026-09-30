import logging
import os
import secrets

logger = logging.getLogger(__name__)


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


def _secret_key():
    key = os.environ.get("SECRET_KEY")
    if not key:
        logger.warning("SECRET_KEY não definida; usando chave aleatória válida apenas para este processo")
        key = secrets.token_hex(32)
    return key


class Settings:
    """Configuração lida do ambiente (ver .env.example)."""

    SECRET_KEY = _secret_key()
    DEBUG = _env_bool("DEBUG")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

    # Endpoints administrativos ficam desligados por padrão.
    ENABLE_ADMIN_ENDPOINTS = _env_bool("ENABLE_ADMIN_ENDPOINTS")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

    APP_VERSION = "1.0.0"
    APP_ENV = os.environ.get("APP_ENV", "producao")
