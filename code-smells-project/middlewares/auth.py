import hmac
from functools import wraps

from flask import current_app, request

from utils.errors import AppError


def require_admin(view):
    """Protege endpoints administrativos: exige flag de ambiente e token no header X-Admin-Token."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        config = current_app.config
        token = request.headers.get("X-Admin-Token", "")
        if (
            not config["ENABLE_ADMIN_ENDPOINTS"]
            or not config["ADMIN_TOKEN"]
            or not hmac.compare_digest(token, config["ADMIN_TOKEN"])
        ):
            raise AppError("Acesso negado", 403)
        return view(*args, **kwargs)

    return wrapper
