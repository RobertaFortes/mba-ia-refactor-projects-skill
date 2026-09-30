"""Valores de negócio que antes estavam repetidos como literais nas rotas."""

TASK_STATUSES = ("pending", "in_progress", "done", "cancelled")
FINISHED_STATUSES = ("done", "cancelled")
DEFAULT_STATUS = "pending"

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_MAX = 2  # prioridades 1 e 2 contam como alta prioridade nos relatórios
PRIORITY_LABELS = {1: "critical", 2: "high", 3: "medium", 4: "low", 5: "minimal"}

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

USER_ROLES = ("user", "admin", "manager")
DEFAULT_ROLE = "user"
ADMIN_ROLE = "admin"
MIN_PASSWORD_LENGTH = 4

DEFAULT_CATEGORY_COLOR = "#000000"

RECENT_ACTIVITY_DAYS = 7
DATE_FORMAT = "%Y-%m-%d"
EMAIL_PATTERN = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
