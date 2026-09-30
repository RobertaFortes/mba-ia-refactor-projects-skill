from flask import jsonify, request

from services import category_service
from utils.errors import ValidationError
from utils.validators import require_json


def get_categories():
    return jsonify(category_service.list_categories()), 200


def create_category():
    data = require_json(request.get_json(silent=True))
    if not data.get('name'):
        raise ValidationError('Nome é obrigatório')
    return jsonify(category_service.create_category(data)), 201


def update_category(cat_id):
    data = require_json(request.get_json(silent=True))
    return jsonify(category_service.update_category(cat_id, data)), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
