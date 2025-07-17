from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models.user import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'message': '需要教师权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def student_or_teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher', 'student']:
            return jsonify({'message': '需要登录'}), 403
        
        return f(*args, **kwargs)
    return decorated_function