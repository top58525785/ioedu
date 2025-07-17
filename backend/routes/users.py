from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app import db
from models.user import User
from utils.decorators import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')
        search = request.args.get('search')
        
        query = User.query
        
        if role:
            query = query.filter(User.role == role)
        
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.email.contains(search))
            )
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 只有管理员或用户本人可以查看用户详情
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'message': '权限不足'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        
        if not username or not email or not password:
            return jsonify({'message': '用户名、邮箱和密码不能为空'}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': '邮箱已存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '用户创建成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # 只有管理员或用户本人可以更新用户信息
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'message': '权限不足'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 普通用户只能更新自己的基本信息
        if current_user.role != 'admin':
            allowed_fields = ['email']
            data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if 'username' in data:
            if User.query.filter(User.username == data['username'], User.id != user_id).first():
                return jsonify({'message': '用户名已存在'}), 400
            user.username = data['username']
        
        if 'email' in data:
            if User.query.filter(User.email == data['email'], User.id != user_id).first():
                return jsonify({'message': '邮箱已存在'}), 400
            user.email = data['email']
        
        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']
        
        if 'is_active' in data and current_user.role == 'admin':
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 不能删除管理员用户
        if user.role == 'admin':
            return jsonify({'message': '不能删除管理员用户'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500