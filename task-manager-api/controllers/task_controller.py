from flask import jsonify, request

from services import task_service
from utils.validators import parse_int_param, validate_task_payload


def get_tasks():
    return jsonify(task_service.list_tasks()), 200


def get_task(task_id):
    return jsonify(task_service.get_task(task_id)), 200


def create_task():
    fields = validate_task_payload(request.get_json(silent=True))
    return jsonify(task_service.create_task(fields)), 201


def update_task(task_id):
    task_service.get_task_or_404(task_id)
    fields = validate_task_payload(request.get_json(silent=True), partial=True)
    return jsonify(task_service.update_task(task_id, fields)), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')
    results = task_service.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_int_param(priority, 'priority') if priority else None,
        user_id=parse_int_param(user_id, 'user_id') if user_id else None,
    )
    return jsonify(results), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
