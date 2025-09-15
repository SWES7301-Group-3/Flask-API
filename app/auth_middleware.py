import requests
from functools import wraps
from flask import request, jsonify, current_app
import jwt

def verify_subscription_token(token):
    """Verify token with Django subscription service"""
    try:
        django_api_url = current_app.config.get('DJANGO_API_URL', 'http://localhost:8000')
        response = requests.post(
            f'{django_api_url}/subscription/api/verify-token/',
            json={'token': token},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                return data
        return None
    except:
        return None

def subscription_required(allowed_roles=None):
    """Decorator to require valid subscription token"""
    if allowed_roles is None:
        allowed_roles = ['user', 'researcher', 'admin']
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    'error': 'Authorization header required',
                    'message': 'Please provide a valid subscription token'
                }), 401
            
            # Extract token
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            
            # Verify token with Django
            token_data = verify_subscription_token(token)
            
            if not token_data:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Please check your subscription token'
                }), 401
            
            # Check role permissions
            user_role = token_data.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This endpoint requires one of: {", ".join(allowed_roles)}'
                }), 403
            
            # Add user data to request context
            request.current_user = token_data
            return f(*args, **kwargs)
        
        return decorated
    return decorator

# Convenience decorators
def user_or_above(f):
    return subscription_required(['user', 'researcher', 'admin'])(f)

def researcher_or_above(f):
    return subscription_required(['researcher', 'admin'])(f)

def admin_only(f):
    return subscription_required(['admin'])(f)