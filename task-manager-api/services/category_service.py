from sqlalchemy import func, select

from config.constants import DEFAULT_CATEGORY_COLOR
from database import db
from models.category import Category
from models.task import Task
from utils.errors import NotFoundError


def _get_or_404(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    counts = dict(db.session.execute(select(Task.category_id, func.count()).group_by(Task.category_id)).all())
    categories = db.session.scalars(select(Category).order_by(Category.id))
    return [dict(c.to_dict(), task_count=counts.get(c.id, 0)) for c in categories]


def create_category(fields):
    category = Category(
        name=fields['name'],
        description=fields.get('description', ''),
        color=fields.get('color', DEFAULT_CATEGORY_COLOR),
    )
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(category_id, fields):
    category = _get_or_404(category_id)
    for name in ('name', 'description', 'color'):
        if name in fields:
            setattr(category, name, fields[name])
    db.session.commit()
    return category.to_dict()


def delete_category(category_id):
    db.session.delete(_get_or_404(category_id))
    db.session.commit()
