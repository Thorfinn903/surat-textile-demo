from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Usage: @roles_required('admin', 'sales')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401) # Unauthorized
            if current_user.role not in roles:
                abort(403) # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Shortcut decorator for admin-only access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
