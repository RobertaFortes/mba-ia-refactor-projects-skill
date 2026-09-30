from flask import Blueprint

from controllers import user_controller as c
from middlewares.auth import require_admin

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', 'get_users', c.get_users, methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', 'get_user', c.get_user, methods=['GET'])
user_bp.add_url_rule('/users', 'create_user', c.create_user, methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', 'update_user', c.update_user, methods=['PUT'])
# Exclusão de usuário (e de suas tasks) é restrita a administradores.
user_bp.add_url_rule('/users/<int:user_id>', 'delete_user', require_admin(c.delete_user), methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', 'get_user_tasks', c.get_user_tasks, methods=['GET'])
user_bp.add_url_rule('/login', 'login', c.login, methods=['POST'])
