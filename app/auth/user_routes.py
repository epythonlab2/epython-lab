# app/auth/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, jwt_required, get_jwt_identity
)
from marshmallow import ValidationError

from app.models.user import User, Role
from app.extensions import db
from .schemas import RegisterSchema, LoginSchema
from .utils import roles_required
from .utils import get_current_user  # Utility to get current user from JWT

# -----------------------------
# Blueprint setup
# -----------------------------
auth_bp = Blueprint('auth', __name__)

# Schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.route('/users/create', methods=['POST'])
@jwt_required(optional=True)
def register():
    """
    Create a new user with role assignment.

    - Anyone can create users with role 'viewer' (default).
    - Only users with 'root' role can assign other roles.
    """
    try:
        data = register_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()

    if existing_user:
        return jsonify({"msg": "User with this username or email already exists"}), 400

    requested_role_name = data.get('role', 'viewer').lower()

    # Check role exists
    role = Role.query.filter_by(name=requested_role_name).first()
    if not role:
        return jsonify({"msg": f"Role '{requested_role_name}' does not exist"}), 400

    # Get current authenticated user (if any)
    current_user = get_current_user()
    print(current_user)
    # print(current_user.role_name)

    if requested_role_name == 'admin':
        # Only root can assign admin role
        if not current_user or not current_user.has_role('root'):
            return jsonify({"msg": "Insufficient permissions to assign admin role"}), 403

    elif requested_role_name == 'editor':
        # Allow both root and admin to assign editor role
        if not current_user or not (current_user.has_role('root') or current_user.has_role('admin')):
            return jsonify({"msg": "Insufficient permissions to assign editor role"}), 403

    # Create user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
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

    access_token = create_access_token(identity=user.username)
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
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)


# -----------------------------
# Assign Role to User
# -----------------------------
@auth_bp.route('/assign-role', methods=['POST'])
@roles_required('admin')
def assign_role():
    data = request.json
    username = data.get('username')
    role_name = data.get('role')

    if not username or not role_name:
        return jsonify({"msg": "username and role required"}), 400

    user = User.query.filter_by(username=username).first()
    role = Role.query.filter_by(name=role_name).first()

    if not user or not role:
        return jsonify({"msg": "User or role not found"}), 404

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()

    return jsonify({"msg": f"Role '{role_name}' assigned to {username}"}), 200


# -----------------------------
# List, Update, Delete Users (Admin)
# -----------------------------
@auth_bp.route('/users', methods=['GET'])
@roles_required('root')
def get_users():
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    query = User.query.order_by(User.created_at.desc())
    total = query.count()

    users = query.limit(limit).offset(offset).all()
    return jsonify({
        "total": total,
        "users": [user.to_dict() for user in users]
    })


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@roles_required('admin')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [r.name for r in user.roles]
    })


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@roles_required('admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)
    db.session.commit()
    return jsonify({"msg": "User updated successfully"})


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@roles_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted successfully"})


# -----------------------------
# Logout
# -----------------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(resp)
    return resp
