# app/auth/utils.py

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from app.models.user import User

def roles_required(*required_roles):
    """
    Decorator to protect routes by requiring specific user roles.

    Usage:
        @roles_required('admin')
        def protected_view():
            ...

    Args:
        *required_roles: One or more role names that the user must have at least one of.

    Returns:
        A 403 Forbidden response if the user lacks the role,
        or 404 if the user is not found.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # Ensure JWT is present and valid
            verify_jwt_in_request()

            # Get identity from JWT
            username = get_jwt_identity()
            user = User.query.filter_by(username=username).first()

            if not user:
                return jsonify({"msg": "User not found"}), 404

            # Check if user has at least one required role
            user_roles = {role.name for role in user.roles}
            if not user_roles.intersection(required_roles):
                return jsonify({"msg": "Access forbidden: insufficient role"}), 403

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# JWT contains username
def get_current_user():
    username = get_jwt_identity()
    return User.query.filter_by(username=username).first()
