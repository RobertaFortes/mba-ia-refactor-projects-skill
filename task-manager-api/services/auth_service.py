from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from models.user import User
from utils.errors import AuthenticationError, ForbiddenError

_SALT = "task-manager-auth"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT)


def issue_token(user):
    return _serializer().dumps({"user_id": user.id})


def user_from_token(token):
    try:
        payload = _serializer().loads(token, max_age=current_app.config["TOKEN_MAX_AGE_SECONDS"])
    except (BadSignature, SignatureExpired):
        raise AuthenticationError("Token inválido ou expirado")
    user = db.session.get(User, payload["user_id"])
    if user is None or not user.active:
        raise AuthenticationError("Token inválido ou expirado")
    return user


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise AuthenticationError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")
    db.session.commit()  # persiste a migração de hash legado, se houve
    return user
