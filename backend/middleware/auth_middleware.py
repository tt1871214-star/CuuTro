import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # If no token passed
        if not token:
            return jsonify({'message': 'Yêu cầu token xác thực.'}), 401
        
        try:
            # Decode using configuration secret key
            secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-relief-platform')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            if payload.get('type') != 'access':
                return jsonify({'message': 'Access token không hợp lệ.'}), 401
                
            user_id = payload.get('identity')
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({'message': 'Người dùng không tồn tại.'}), 401
                
            if not current_user.is_active:
                return jsonify({'message': 'Tài khoản đã bị vô hiệu hóa.'}), 401
                
            # Store user in flask request local namespace
            request.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token đã hết hạn.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token không hợp lệ.'}), 401
            
        return f(*args, **kwargs)
    return decorated

def roles_accepted(*role_names):
    """Decorator to limit endpoint access to specified user roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Ensure token_required is executed first
            if not hasattr(request, 'current_user'):
                return jsonify({'message': 'Lỗi xác thực người dùng.'}), 401
                
            user_role = request.current_user.role.name if request.current_user.role else None
            
            if user_role not in role_names:
                return jsonify({'message': 'Bạn không có quyền thực hiện hành động này.'}), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator
