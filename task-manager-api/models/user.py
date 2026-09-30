import hashlib
import re

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import ADMIN_ROLE, DEFAULT_ROLE
from database import db
from utils.time import utcnow

_LEGACY_MD5 = re.compile(r"^[0-9a-f]{32}$")


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        """Representação pública: o hash da senha nunca sai na API."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        """Confere a senha; hashes MD5 legados são aceitos uma vez e migrados para o novo formato."""
        if _LEGACY_MD5.match(self.password or ''):
            if self.password == hashlib.md5(pwd.encode()).hexdigest():
                self.set_password(pwd)
                return True
            return False
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == ADMIN_ROLE
