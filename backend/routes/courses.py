from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.course import Course
from utils.decorators import teacher_required, admin_required

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        teacher_id = request.args.get('teacher_id', type=int)
        
        query = Course.query
        
        # 学生只能看到自己班级的课程，教师只能看到自己的课程
        if current_user.role == 'student':
            # TODO: 根据学生班级过滤课程
            pass
        elif current_user.role == 'teacher':
            query = query.filter(Course.teacher_id == current_user_id)
        
        if search:
            query = query.filter(
                (Course.name.contains(search)) |
                (Course.code.contains(search))
            )
        
        if teacher_id and current_user.role == 'admin':
            query = query.filter(Course.teacher_id == teacher_id)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        courses = [course.to_dict() for course in pagination.items]
        
        return jsonify({
            'courses': courses,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # TODO: 权限检查
        
        return jsonify({'course': course.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@courses_bp.route('/', methods=['POST'])
@jwt_required()
@teacher_required
def create_course():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        name = data.get('name')
        code = data.get('code')
        description = data.get('description', '')
        semester = data.get('semester')
        teacher_id = data.get('teacher_id', current_user_id)
        
        if not name or not code or not semester:
            return jsonify({'message': '课程名称、代码和学期不能为空'}), 400
        
        # 管理员可以指定教师，教师只能创建自己的课程
        if current_user.role != 'admin':
            teacher_id = current_user_id
        
        # 检查课程代码是否已存在
        if Course.query.filter_by(code=code).first():
            return jsonify({'message': '课程代码已存在'}), 400
        
        course = Course(
            name=name,
            code=code,
            description=description,
            teacher_id=teacher_id,
            semester=semester
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': '课程创建成功',
            'course': course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 只有课程教师或管理员可以修改课程
        if current_user.role != 'admin' and course.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        if 'name' in data:
            course.name = data['name']
        
        if 'code' in data:
            if Course.query.filter(Course.code == data['code'], Course.id != course_id).first():
                return jsonify({'message': '课程代码已存在'}), 400
            course.code = data['code']
        
        if 'description' in data:
            course.description = data['description']
        
        if 'semester' in data:
            course.semester = data['semester']
        
        if 'status' in data:
            course.status = data['status']
        
        if 'teacher_id' in data and current_user.role == 'admin':
            course.teacher_id = data['teacher_id']
        
        db.session.commit()
        
        return jsonify({
            'message': '课程更新成功',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 只有课程教师或管理员可以删除课程
        if current_user.role != 'admin' and course.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': '课程删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500