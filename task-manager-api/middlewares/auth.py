from functools import wraps

from flask import request

from services import auth_service
from utils.errors import AuthenticationError, ForbiddenError


def current_user(required=False):
    """Usuário do header `Authorization: Bearer <token>` (ou None quando ausente e não obrigatório)."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        if required:
            raise AuthenticationError("Autenticação necessária")
        return None
    return auth_service.user_from_token(header[len("Bearer "):])


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user(required=True).is_admin():
            raise ForbiddenError("Acesso restrito a administradores")
        return view(*args, **kwargs)

    return wrapper
