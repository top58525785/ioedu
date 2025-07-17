from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.class_model import Class, StudentClass, ClassCourse
from models.course import Course
from utils.decorators import teacher_required, admin_required

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/', methods=['GET'])
@jwt_required()
def get_classes():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        
        query = Class.query
        
        # 学生只能看到自己加入的班级
        if current_user.role == 'student':
            enrolled_classes = db.session.query(StudentClass.class_id).filter_by(student_id=current_user_id).subquery()
            query = query.filter(Class.id.in_(enrolled_classes))
        elif current_user.role == 'teacher':
            # 教师只能看到自己创建的班级
            query = query.filter(Class.teacher_id == current_user_id)
        
        if search:
            query = query.filter(Class.name.contains(search))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        classes = [class_obj.to_dict() for class_obj in pagination.items]
        
        return jsonify({
            'classes': classes,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@classes_bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def get_class(class_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({'message': '班级不存在'}), 404
        
        # 权限检查
        if current_user.role == 'student':
            enrollment = StudentClass.query.filter_by(
                student_id=current_user_id, 
                class_id=class_id
            ).first()
            if not enrollment:
                return jsonify({'message': '权限不足'}), 403
        elif current_user.role == 'teacher' and class_obj.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        # 获取班级学生列表
        students = []
        for enrollment in class_obj.student_enrollments:
            student_data = enrollment.student.to_dict()
            student_data['enrolled_at'] = enrollment.enrolled_at.isoformat()
            students.append(student_data)
        
        class_data = class_obj.to_dict()
        class_data['students'] = students
        
        return jsonify({'class': class_data}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@classes_bp.route('/', methods=['POST'])
@jwt_required()
@teacher_required
def create_class():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        teacher_id = data.get('teacher_id', current_user_id)
        
        if not name:
            return jsonify({'message': '班级名称不能为空'}), 400
        
        # 管理员可以指定教师，教师只能创建自己的班级
        if current_user.role != 'admin':
            teacher_id = current_user_id
        
        class_obj = Class(
            name=name,
            description=description,
            teacher_id=teacher_id
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({
            'message': '班级创建成功',
            'class': class_obj.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@classes_bp.route('/<int:class_id>/students', methods=['POST'])
@jwt_required()
@teacher_required
def add_student_to_class(class_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({'message': '班级不存在'}), 404
        
        # 检查权限
        if current_user.role != 'admin' and class_obj.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'message': '学生ID不能为空'}), 400
        
        # 检查学生是否存在
        student = User.query.filter_by(id=student_id, role='student').first()
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        # 检查是否已经加入班级
        existing = StudentClass.query.filter_by(
            student_id=student_id, 
            class_id=class_id
        ).first()
        if existing:
            return jsonify({'message': '学生已在班级中'}), 400
        
        enrollment = StudentClass(
            student_id=student_id,
            class_id=class_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({'message': '学生添加成功'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@classes_bp.route('/<int:class_id>/join', methods=['POST'])
@jwt_required()
def join_class(class_id):
    """学生加入班级"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'student':
            return jsonify({'message': '只有学生可以加入班级'}), 403
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({'message': '班级不存在'}), 404
        
        # 检查是否已经加入班级
        existing = StudentClass.query.filter_by(
            student_id=current_user_id, 
            class_id=class_id
        ).first()
        if existing:
            return jsonify({'message': '已在班级中'}), 400
        
        enrollment = StudentClass(
            student_id=current_user_id,
            class_id=class_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({'message': '加入班级成功'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500