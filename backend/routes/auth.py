from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
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
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'message': '旧密码和新密码不能为空'}), 400
        
        if not user.check_password(old_password):
            return jsonify({'message': '旧密码错误'}), 400
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500