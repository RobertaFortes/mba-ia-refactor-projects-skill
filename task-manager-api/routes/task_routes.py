from flask import Blueprint

from controllers import task_controller as c

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', 'get_tasks', c.get_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'get_task', c.get_task, methods=['GET'])
task_bp.add_url_rule('/tasks', 'create_task', c.create_task, methods=['POST'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'update_task', c.update_task, methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'delete_task', c.delete_task, methods=['DELETE'])
task_bp.add_url_rule('/tasks/search', 'search_tasks', c.search_tasks, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', 'task_stats', c.task_stats, methods=['GET'])
