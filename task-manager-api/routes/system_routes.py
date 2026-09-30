from flask import Blueprint

from controllers import system_controller as c

system_bp = Blueprint('system', __name__)

system_bp.add_url_rule('/health', 'health', c.health, methods=['GET'])
system_bp.add_url_rule('/', 'index', c.index, methods=['GET'])
