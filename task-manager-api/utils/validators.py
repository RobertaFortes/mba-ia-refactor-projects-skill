import re
from datetime import datetime

from config.constants import (
    DATE_FORMAT,
    EMAIL_PATTERN,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    TASK_STATUSES,
    USER_ROLES,
)
from utils.errors import ValidationError


def require_json(data):
    if not data or not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    return data


def parse_date(value):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")


def normalize_tags(tags):
    return ",".join(tags) if isinstance(tags, list) else tags


def _validate_title(title):
    if not isinstance(title, str):
        raise ValidationError("Título inválido")
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return title


def _validate_status(status):
    if status not in TASK_STATUSES:
        raise ValidationError("Status inválido")
    return status


def _validate_priority(priority):
    if not isinstance(priority, int) or isinstance(priority, bool) or not MIN_PRIORITY <= priority <= MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")
    return priority


def validate_task_payload(data, partial=False):
    """Valida o corpo de POST/PUT de tasks e devolve apenas os campos informados (já normalizados)."""
    data = require_json(data)
    fields = {}

    if not partial and not data.get("title"):
        raise ValidationError("Título é obrigatório")
    if "title" in data:
        fields["title"] = _validate_title(data["title"])
    if "description" in data:
        fields["description"] = data["description"]
    if "status" in data:
        fields["status"] = _validate_status(data["status"])
    if "priority" in data:
        fields["priority"] = _validate_priority(data["priority"])
    if "user_id" in data:
        fields["user_id"] = data["user_id"]
    if "category_id" in data:
        fields["category_id"] = data["category_id"]
    if "due_date" in data:
        fields["due_date"] = parse_date(data["due_date"]) if data["due_date"] else None
    if "tags" in data:
        fields["tags"] = normalize_tags(data["tags"])
    return fields


def validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError("Email inválido")
    return email


def validate_password(password, message):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return password


def validate_role(role):
    if role not in USER_ROLES:
        raise ValidationError("Role inválido")
    return role


def parse_int_param(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Parâmetro {name} inválido")
