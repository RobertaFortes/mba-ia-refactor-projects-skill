from sqlalchemy import func, select

from config.constants import DEFAULT_ROLE
from database import db
from models.task import Task
from models.user import User
from services import auth_service
from utils.errors import ConflictError, ForbiddenError, NotFoundError


def get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')
    return user


def list_users():
    counts = dict(db.session.execute(select(Task.user_id, func.count()).group_by(Task.user_id)).all())
    users = db.session.scalars(select(User).order_by(User.id))
    return [dict(user.to_dict(), task_count=counts.get(user.id, 0)) for user in users]


def get_user(user_id):
    user = get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in sorted(user.tasks, key=lambda t: t.id)]
    return data


def _ensure_email_available(email, ignore_user_id=None):
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != ignore_user_id:
        raise ConflictError('Email já cadastrado')


def create_user(fields, acting_user):
    """Somente administradores autenticados podem criar usuários com role diferente do padrão."""
    _ensure_email_available(fields['email'])
    role = fields.get('role', DEFAULT_ROLE)
    if role != DEFAULT_ROLE and not (acting_user and acting_user.is_admin()):
        raise ForbiddenError('Apenas administradores podem definir roles')

    user = User(name=fields['name'], email=fields['email'], role=role)
    user.set_password(fields['password'])
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, fields, acting_user):
    user = get_user_or_404(user_id)
    if 'email' in fields:
        _ensure_email_available(fields['email'], ignore_user_id=user_id)
    if 'role' in fields and not (acting_user and acting_user.is_admin()):
        raise ForbiddenError('Apenas administradores podem alterar roles')

    for name in ('name', 'email', 'role', 'active'):
        if name in fields:
            setattr(user, name, fields[name])
    if 'password' in fields:
        user.set_password(fields['password'])
    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    """Remove o usuário e suas tasks na mesma transação (comportamento original, agora explícito)."""
    user = get_user_or_404(user_id)
    for task in list(user.tasks):
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()


def list_user_tasks(user_id):
    user = get_user_or_404(user_id)
    return [task.to_summary_dict() for task in sorted(user.tasks, key=lambda t: t.id)]


def login(email, password):
    user = auth_service.authenticate(email, password)
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': auth_service.issue_token(user),
    }
