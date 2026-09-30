from flask import Blueprint

from controllers import sistema_controller as c
from middlewares.auth import require_admin

sistema_bp = Blueprint("sistema", __name__)

sistema_bp.add_url_rule("/", "index", c.index, methods=["GET"])
sistema_bp.add_url_rule("/health", "health_check", c.health_check, methods=["GET"])
# Endpoint destrutivo: exige ENABLE_ADMIN_ENDPOINTS=true + header X-Admin-Token.
sistema_bp.add_url_rule("/admin/reset-db", "reset_database", require_admin(c.reset_database), methods=["POST"])
