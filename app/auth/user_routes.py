from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, jwt_required
)
from marshmallow import ValidationError

from app.models.user import User, Role
from app.extensions import db
from .schemas import RegisterSchema, LoginSchema
from .utils import roles_required, get_current_user
from datetime import timedelta
# -----------------------------
# Blueprint Setup
# -----------------------------
auth_bp = Blueprint('auth', __name__)

# Schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()


# -----------------------------
# Register User (Create New User)
# -----------------------------
@auth_bp.route('/users/create', methods=['POST'])
@jwt_required()
def register():
    """Create a new user with role assignment."""
    try:
        data = register_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check for existing user
    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({"msg": "User with this username or email already exists"}), 400

    requested_role_name = data.get('role', 'viewer').lower()
    current_user = get_current_user()

    role = get_role_for_current_user(current_user, requested_role_name)
    if not role:
        return jsonify({"msg": f"Role '{requested_role_name}' does not exist or insufficient permissions."}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])  # Ensure password is hashed before storing it
    user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role.name
        }
    }), 201


def get_role_for_current_user(current_user, requested_role_name):
    """Returns the role for the current user based on permissions."""
    if current_user.has_role('root'):
        return Role.query.filter_by(name=requested_role_name).first()
    elif current_user.has_role('admin') and requested_role_name not in ['admin', 'root']:
        return Role.query.filter_by(name=requested_role_name).first()
    return None


# -----------------------------
# User Login
# -----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid username or password"}), 401

    # Implement access token expiration (e.g., 15 minutes for access token)
    access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=user.username)

    resp = jsonify({
        "msg": "Login successful",
        "username": user.username,
        "roles": [role.name for role in user.roles]
    })

    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200


# -----------------------------
# Token Refresh
# -----------------------------
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT token."""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))
    return jsonify(access_token=new_access_token)


# -----------------------------
# List, Update, Delete Users (Admin Only)
# -----------------------------
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Retrieve a list of users with filtering and pagination."""
    current_user = get_current_user()
    limit, offset = int(request.args.get('limit', 10)), int(request.args.get('offset', 0))

    query = User.query
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()

    if search:
        query = query.filter((User.username.ilike(f'%{search}%')) | (User.email.ilike(f'%{search}%')))
    if role:
        query = query.filter(User.roles.any(name=role))
    if status:
        query = query.filter(User.is_active == (status == 'active'))

    if current_user.has_role('root'):
        pass
    elif current_user.has_role('admin'):
        query = query.filter(~User.roles.any(name='admin'), ~User.roles.any(name='root'))
    else:
        return jsonify({"msg": "You do not have permission to view users."}), 403

    total = query.count()
    users = query.limit(limit).offset(offset).all()

    return jsonify({
        "total": total,
        "users": [user.to_dict() for user in users]
    })


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_current_user()
    user = User.query.get_or_404(user_id)

    if current_user.has_role('root'):
        pass  # Root users can view any user
    elif current_user.has_role('admin'):
        if user.has_role('admin') or user.has_role('root'):
            return jsonify({"msg": "You do not have permission to view this user's details."}), 403
    else:
        return jsonify({"msg": "You do not have permission to view user details."}), 403

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [r.name for r in user.roles]
    })


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user details and roles."""
    user = User.query.get_or_404(user_id)
    data = request.json
    current_user = get_current_user()

    if current_user.has_role('root'):
        update_user_details(user, data)
        update_user_roles(user, data.get('roles', []))
    elif current_user.has_role('admin') and not (user.has_role('root') or user.has_role('admin')):
        update_user_details(user, data)
        if 'roles' in data:
            roles = data['roles']
            if any(role in ['admin', 'root'] for role in roles):
                return jsonify({"msg": "Admins cannot assign 'admin' or 'root' roles."}), 403
            update_user_roles(user, roles)
    else:
        return jsonify({"msg": "Insufficient permissions to update user."}), 403

    db.session.commit()

    return jsonify({
        "msg": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles]
        }
    })


def update_user_details(user, data):
    """Update the basic details of the user."""
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)


def update_user_roles(user, roles):
    """Update the roles of the user."""
    user.roles = []  # Clear existing roles
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.roles.append(role)


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    current_user = get_current_user()

    if current_user.has_role('root'):
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"})
    elif current_user.has_role('admin') and not (user.has_role('root') or user.has_role('admin')):
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"})

    return jsonify({"msg": "Insufficient permissions to delete user."}), 403


# -----------------------------
# Logout
# -----------------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(resp)
    return resp
