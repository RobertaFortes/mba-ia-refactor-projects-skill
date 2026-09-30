from flask import Blueprint

from controllers import category_controller as c

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', 'get_categories', c.get_categories, methods=['GET'])
category_bp.add_url_rule('/categories', 'create_category', c.create_category, methods=['POST'])
category_bp.add_url_rule('/categories/<int:cat_id>', 'update_category', c.update_category, methods=['PUT'])
category_bp.add_url_rule('/categories/<int:cat_id>', 'delete_category', c.delete_category, methods=['DELETE'])
