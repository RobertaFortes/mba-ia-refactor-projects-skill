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
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = _env_bool("DEBUG")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    TOKEN_MAX_AGE_SECONDS = int(os.environ.get("TOKEN_MAX_AGE_SECONDS", 8 * 3600))
