from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, jwt_required, get_jwt_identity
)
from marshmallow import ValidationError
from datetime import timedelta

from app.models.user import User, Role
from app.models.log import AuditLog
from app.extensions import db
from .schemas import RegisterSchema, LoginSchema
from .utils import roles_required, get_current_user
from app.utils.logging_utils import (
    log_session, log_audit_action, update_last_activity,
    format_last_login
)

auth_bp = Blueprint('auth', __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


def get_role_for_current_user(current_user, requested_role_name):
    """
    Determine if the current user has permission to assign the requested role.

    Args:
        current_user (User): The user making the request.
        requested_role_name (str): The role name requested for assignment.

    Returns:
        Role or None: Role object if permitted; otherwise None.
    """
    if current_user.has_role('root'):
        return Role.query.filter_by(name=requested_role_name).first()
    elif current_user.has_role('admin') and requested_role_name not in ['admin', 'root']:
        return Role.query.filter_by(name=requested_role_name).first()
    return None


@auth_bp.route('/users/create', methods=['POST'])
@jwt_required()
def register():
    """
    Register a new user with specified role, username, email, and password.
    Enforces role-based assignment permissions.

    Returns:
        JSON response with success message and user info or error details.
    """
    try:
        data = register_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check for existing username or email
    if User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first():
        return jsonify({"msg": "User with this username or email already exists"}), 400

    requested_role_name = data.get('role', 'viewer').lower()
    current_user = get_current_user()

    role = get_role_for_current_user(current_user, requested_role_name)
    if not role:
        return jsonify({"msg": f"Role '{requested_role_name}' does not exist or insufficient permissions."}), 400

    # Create new user and assign role
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    user.roles.append(role)
    db.session.add(user)
    db.session.commit()

    # Log the user creation action for auditing
    log_audit_action(
        actor_id=current_user.id,
        target_user_id=user.id,
        action_type='create',
        description=f"Created user '{user.username}' with role '{role.name}'"
    )

    return jsonify({
        "msg": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role.name
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user credentials and issue JWT access and refresh tokens.
    Also logs user session for auditing.

    Returns:
        JSON response with login success, username, roles and sets JWT cookies.
    """
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid username or password"}), 401

    if not user.is_active:
        return jsonify({"msg": "Your account is inactive. Please contact an administrator."}), 403

    access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=user.username)

    # Log session for auditing
    log_session(user)

    resp = jsonify({
        "msg": "Login successful",
        "username": user.username,
        "roles": [role.name for role in user.roles]
    })

    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the JWT access token using a valid refresh token.

    Returns:
        JSON response with new access token.
    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))
    return jsonify(access_token=new_access_token)


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Retrieve a paginated list of users filtered by optional search, role, and status.
    Enforces role-based visibility restrictions.

    Query Parameters:
        limit (int): Number of users to return (default 10).
        offset (int): Number of users to skip (default 0).
        search (str): Search keyword for username or email.
        role (str): Filter users by role name.
        status (str): Filter by active status ('active' or 'inactive').

    Returns:
        JSON response with total user count and list of user data including formatted last login.
    """
    current_user = get_current_user()
    update_last_activity(current_user)

    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()

    query = User.query

    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) | (User.email.ilike(f'%{search}%'))
        )

    if role:
        query = query.filter(User.roles.any(name=role))

    if status:
        is_active = (status.lower() == 'active')
        query = query.filter(User.is_active == is_active)

    # Enforce role-based restrictions
    if current_user.has_role('root'):
        pass  # No restrictions
    elif current_user.has_role('admin'):
        query = query.filter(~User.roles.any(name='admin'), ~User.roles.any(name='root'))
    else:
        return jsonify({"msg": "You do not have permission to view users."}), 403

    total = query.count()
    users = query.limit(limit).offset(offset).all()

    return jsonify({
        "total": total,
        "users": [
            dict(
                user.to_dict(),
                last_login=format_last_login(
                    user.session_logs[-1].login_time.isoformat() if user.session_logs else None
                )
            ) for user in users
        ]
    })


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Retrieve detailed information about a specific user by ID.
    Enforces role-based access control.

    Args:
        user_id (int): ID of the user to retrieve.

    Returns:
        JSON response with user details or an error message.
    """
    current_user = get_current_user()
    update_last_activity(current_user)

    user = User.query.get_or_404(user_id)

    if current_user.has_role('root'):
        pass  # Full access
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
        "roles": [role.name for role in user.roles]
    })


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update user details and roles, enforcing role-based permissions.

    Args:
        user_id (int): ID of the user to update.

    Returns:
        JSON response with success message and updated user info or error.
    """
    user = User.query.get_or_404(user_id)
    data = request.json
    current_user = get_current_user()
    update_last_activity(current_user)

    old_roles = [role.name for role in user.roles]
    old_status = user.is_active

    # Role and permission checks before update
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

    new_roles = [role.name for role in user.roles]
    new_status = user.is_active

    # Track changes for audit logging
    changes = []
    if old_roles != new_roles:
        changes.append(f"Roles changed from {old_roles} to {new_roles}")
    if old_status != new_status:
        changes.append(
            f"Status changed from {'active' if old_status else 'inactive'} "
            f"to {'active' if new_status else 'inactive'}"
        )

    if changes:
        log_audit_action(
            actor_id=current_user.id,
            target_user_id=user.id,
            action_type='update',
            description='; '.join(changes)
        )

    return jsonify({
        "msg": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": new_roles
        }
    })


def update_user_details(user, data):
    """
    Helper function to update user's basic information.

    Args:
        user (User): User object to update.
        data (dict): Dictionary with update fields.
    """
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)


def update_user_roles(user, roles):
    """
    Helper function to update user's roles.

    Args:
        user (User): User object to update.
        roles (list): List of role names to assign.
    """
    user.roles = []
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.roles.append(role)


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a user by ID with permission checks and audit logging.

    Args:
        user_id (int): ID of the user to delete.

    Returns:
        JSON response with success or error message.
    """
    user = User.query.get_or_404(user_id)
    current_user = get_current_user()
    update_last_activity(current_user)

    if current_user.has_role('root') or \
       (current_user.has_role('admin') and not (user.has_role('root') or user.has_role('admin'))):

        log_audit_action(
            actor_id=current_user.id,
            target_user_id=user.id,
            action_type='delete',
            description=f"Deleted user '{user.username}'"
        )
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"})

    return jsonify({"msg": "Insufficient permissions to delete user."}), 403

#
# @auth_bp.route('/audit/logs', methods=['GET'])
# @jwt_required()
# def get_audit_logs():
#     """
#     Retrieve the latest 100 audit log entries.
#     Only accessible to users with 'admin' or 'root' roles.
#
#     Returns:
#         JSON list of audit log entries.
#     """
#     current_user = get_current_user()
#     if not current_user.has_role('admin') and not current_user.has_role('root'):
#         return jsonify({"msg": "You do not have permission to view audit logs."}), 403
#
#     logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
#     return jsonify([{
#         "id": log.id,
#         "action_type": log.action_type,
#         "actor": log.actor.username if log.actor else None,
#         "target_user": log.target_user.username if log.target_user else None,
#         "description": log.description,
#         "timestamp": log.timestamp.isoformat()
#     } for log in logs])


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logs out the user by unsetting JWT cookies.

    Returns:
        JSON response confirming logout.
    """
    resp = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(resp)
    return resp
