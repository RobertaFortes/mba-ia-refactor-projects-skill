from flask import jsonify, request

from middlewares.auth import current_user
from services import user_service
from utils.errors import ValidationError
from utils.validators import require_json, validate_email, validate_password, validate_role


def get_users():
    return jsonify(user_service.list_users()), 200


def get_user(user_id):
    return jsonify(user_service.get_user(user_id)), 200


def create_user():
    data = require_json(request.get_json(silent=True))
    for field, message in (('name', 'Nome é obrigatório'), ('email', 'Email é obrigatório'), ('password', 'Senha é obrigatória')):
        if not data.get(field):
            raise ValidationError(message)

    fields = {
        'name': data['name'],
        'email': validate_email(data['email']),
        'password': validate_password(data['password'], 'Senha deve ter no mínimo 4 caracteres'),
    }
    if 'role' in data:
        fields['role'] = validate_role(data['role'])
    return jsonify(user_service.create_user(fields, current_user())), 201


def update_user(user_id):
    user_service.get_user_or_404(user_id)
    data = require_json(request.get_json(silent=True))

    fields = {}
    if 'name' in data:
        fields['name'] = data['name']
    if 'email' in data:
        fields['email'] = validate_email(data['email'])
    if 'password' in data:
        fields['password'] = validate_password(data['password'], 'Senha muito curta')
    if 'role' in data:
        fields['role'] = validate_role(data['role'])
    if 'active' in data:
        fields['active'] = data['active']
    return jsonify(user_service.update_user(user_id, fields, current_user())), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    return jsonify(user_service.list_user_tasks(user_id)), 200


def login():
    data = require_json(request.get_json(silent=True))
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    return jsonify(user_service.login(email, password)), 200
