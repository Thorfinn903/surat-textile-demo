import jwt
import datetime
from flask import current_app, request, g
from functools import wraps
from ..models import User
from .responses import error_response

def generate_tokens(user_id, role):
    """
    Generates short-lived Access Token (1 hour) and a Refresh Token (7 days).
    """
    try:
        # Access Token
        access_payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow(),
            'sub': str(user_id),
            'role': role,
            'type': 'access'
        }
        access_token = jwt.encode(
            access_payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

        # Refresh Token
        refresh_payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'sub': str(user_id),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except Exception as e:
        return None

def token_required(roles=None):
    """
    Decorator for API endpoints to enforce JWT and Role based security.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return error_response(message='Bearer token malformed', status_code=401)

            if not token:
                return error_response(message='Token is missing', status_code=401)

            try:
                payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
                
                if payload.get('type') != 'access':
                    return error_response(message='Invalid token type. Expected access token.', status_code=401)
                
                user_id = payload['sub']
                user_role = payload.get('role')
                
                if roles and user_role not in roles:
                    return error_response(message='Insufficient permissions. Admin role required.', status_code=403)
                
                # Expose safely
                g.current_user_id = user_id
                g.current_user_role = user_role
                
            except jwt.ExpiredSignatureError:
                return error_response(message='Token expired. Please use refresh token.', status_code=401)
            except jwt.InvalidTokenError as e:
                print("JWT INVALID TOKEN ERROR:", str(e))
                return error_response(message='Invalid token. Please authenticate.', status_code=401)

            return f(*args, **kwargs)

        return decorated
    return decorator
