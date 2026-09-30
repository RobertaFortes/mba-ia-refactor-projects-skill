from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from config.constants import DEFAULT_PRIORITY, DEFAULT_STATUS, FINISHED_STATUSES
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import NotFoundError
from utils.time import utcnow


def _ensure_user_exists(user_id):
    if user_id and db.session.get(User, user_id) is None:
        raise NotFoundError('Usuário não encontrado')


def _ensure_category_exists(category_id):
    if category_id and db.session.get(Category, category_id) is None:
        raise NotFoundError('Categoria não encontrada')


def get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    return task


def list_tasks():
    # joinedload evita o N+1 de buscar usuário e categoria task a task
    stmt = select(Task).options(joinedload(Task.user), joinedload(Task.category)).order_by(Task.id)
    result = []
    for task in db.session.scalars(stmt).unique():
        data = task.to_detail_dict()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        result.append(data)
    return result


def get_task(task_id):
    return get_task_or_404(task_id).to_detail_dict()


def create_task(fields):
    _ensure_user_exists(fields.get('user_id'))
    _ensure_category_exists(fields.get('category_id'))

    task = Task(
        title=fields['title'],
        description=fields.get('description', ''),
        status=fields.get('status', DEFAULT_STATUS),
        priority=fields.get('priority', DEFAULT_PRIORITY),
        user_id=fields.get('user_id'),
        category_id=fields.get('category_id'),
        due_date=fields.get('due_date'),
        tags=fields.get('tags') or None,
    )
    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, fields):
    task = get_task_or_404(task_id)
    _ensure_user_exists(fields.get('user_id'))
    _ensure_category_exists(fields.get('category_id'))

    for name, value in fields.items():
        setattr(task, name, value)
    task.updated_at = utcnow()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = get_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()


def search_tasks(query='', status='', priority=None, user_id=None):
    stmt = select(Task)
    if query:
        stmt = stmt.where(or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
    if status:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if user_id is not None:
        stmt = stmt.where(Task.user_id == user_id)
    return [task.to_dict() for task in db.session.scalars(stmt.order_by(Task.id))]


def task_stats():
    by_status = dict(db.session.execute(select(Task.status, func.count()).group_by(Task.status)).all())
    total = sum(by_status.values())
    overdue = db.session.scalar(
        select(func.count()).select_from(Task).where(Task.due_date < utcnow(), Task.status.notin_(FINISHED_STATUSES))
    )
    done = by_status.get('done', 0)
    return {
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': overdue,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
