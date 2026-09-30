from datetime import timedelta

from sqlalchemy import case, func, select

from config.constants import FINISHED_STATUSES, HIGH_PRIORITY_MAX, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import NotFoundError
from utils.time import utcnow


def _percentage(part, total):
    return round((part / total) * 100, 2) if total > 0 else 0


def _count(model, *conditions):
    return db.session.scalar(select(func.count()).select_from(model).where(*conditions))


def summary_report():
    now = utcnow()
    by_status = dict(db.session.execute(select(Task.status, func.count()).group_by(Task.status)).all())
    by_priority = dict(db.session.execute(select(Task.priority, func.count()).group_by(Task.priority)).all())

    overdue_tasks = db.session.scalars(
        select(Task).where(Task.due_date < now, Task.status.notin_(FINISHED_STATUSES)).order_by(Task.id)
    ).all()

    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    # Produtividade por usuário em UMA query (antes: uma query de tasks por usuário)
    done_count = func.coalesce(func.sum(case((Task.status == 'done', 1), else_=0)), 0)
    productivity_rows = db.session.execute(
        select(User.id, User.name, func.count(Task.id), done_count)
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .order_by(User.id)
    ).all()

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': sum(by_status.values()),
            'total_users': _count(User),
            'total_categories': _count(Category),
        },
        'tasks_by_status': {
            'pending': by_status.get('pending', 0),
            'in_progress': by_status.get('in_progress', 0),
            'done': by_status.get('done', 0),
            'cancelled': by_status.get('cancelled', 0),
        },
        'tasks_by_priority': {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': (now - t.due_date).days,
                }
                for t in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': _count(Task, Task.created_at >= since),
            'tasks_completed_last_7_days': _count(Task, Task.status == 'done', Task.updated_at >= since),
        },
        'user_productivity': [
            {
                'user_id': user_id,
                'user_name': name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': _percentage(completed, total),
            }
            for user_id, name, total, completed in productivity_rows
        ],
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    tasks = user.tasks
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == 'done')
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': sum(1 for t in tasks if t.status == 'pending'),
            'in_progress': sum(1 for t in tasks if t.status == 'in_progress'),
            'cancelled': sum(1 for t in tasks if t.status == 'cancelled'),
            'overdue': sum(1 for t in tasks if t.is_overdue()),
            'high_priority': sum(1 for t in tasks if t.priority <= HIGH_PRIORITY_MAX),
            'completion_rate': _percentage(done, total),
        },
    }
