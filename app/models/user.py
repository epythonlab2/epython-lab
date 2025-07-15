# app/models/user.py

from datetime import datetime
from app.extensions import db, bcrypt

# Association table for many-to-many relationship between User and Role
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


class User(db.Model):
    """User model representing registered users."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # <-- Add this line
    # Many-to-many relationship: users <-> roles
    roles = db.relationship('Role', secondary=user_roles, backref='users', lazy='dynamic')

    def set_password(self, password):
        """Hashes and sets the user password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Validates the password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        """Checks if the user has a specific role."""
        return self.roles.filter(Role.name == role_name).count() > 0

    def get_role_names(self):
        """Returns a list of role names assigned to the user."""
        return [role.name for role in self.roles]

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "roles": [role.name for role in self.roles]
        }


class Role(db.Model):
    """Role model for user permissions/roles."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"
