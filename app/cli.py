# app/cli.py

import os
import click
from flask.cli import with_appcontext

from app.models.user import User, Role
from app.extensions import db

@click.command("seed-roles")
@with_appcontext
def seed_roles():
    """
    Seeds default roles into the roles table: root, admin, editor, viewer.

    Usage:
        flask seed-roles
    """
    default_roles = ["root", "admin", "editor", "viewer"]
    for role_name in default_roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
            click.secho(f"🛠️  Created role '{role_name}'", fg="yellow")
    db.session.commit()
    click.secho("✅ All default roles seeded.", fg="green")

@click.command("create-admin")
@with_appcontext
def create_admin():
    """
    Creates a default admin user using environment variables.

    Environment variables used:
      - ADMIN_USERNAME (default: 'admin')
      - ADMIN_EMAIL (default: 'admin@example.com')
      - ADMIN_PASSWORD (default: 'admin123')

    This command:
      1. Ensures the 'root' role exists.
      2. Creates an admin user with the provided credentials if not already present.
      3. Assigns the 'root' role to the user.

    Usage:
        flask create-admin
    """
    username = os.getenv("ADMIN_USERNAME", "admin")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    # Ensure 'root' role exists
    root_role = Role.query.filter_by(name='root').first()
    if not root_role:
        root_role = Role(name='root')
        db.session.add(root_role)
        db.session.commit()
        click.secho("🛠️  Created 'root' role.", fg="yellow")

    # Create admin user if not already present
    admin_user = User.query.filter_by(username=username).first()
    if not admin_user:
        admin_user = User(username=username, email=email)
        admin_user.set_password(password)
        admin_user.roles.append(root_role)
        db.session.add(admin_user)
        db.session.commit()
        click.secho(f"✅ Admin user '{username}' created successfully.", fg="green")
    else:
        click.secho("ℹ️  Admin user already exists. No changes made.", fg="blue")
