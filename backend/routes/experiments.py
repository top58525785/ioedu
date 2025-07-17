from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.course import Course
from models.experiment import Experiment, ExperimentStep, DataPoint
from utils.decorators import teacher_required

experiments_bp = Blueprint('experiments', __name__)

@experiments_bp.route('/', methods=['GET'])
@jwt_required()
def get_experiments():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        course_id = request.args.get('course_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = Experiment.query
        
        # 学生只能看到已发布的实验
        if current_user.role == 'student':
            query = query.filter(Experiment.status.in_(['published', 'active']))
        elif current_user.role == 'teacher':
            # 教师只能看到自己课程的实验
            teacher_courses = Course.query.filter_by(teacher_id=current_user_id).all()
            course_ids = [course.id for course in teacher_courses]
            query = query.filter(Experiment.course_id.in_(course_ids))
        
        if course_id:
            query = query.filter(Experiment.course_id == course_id)
        
        if status:
            query = query.filter(Experiment.status == status)
        
        if search:
            query = query.filter(Experiment.title.contains(search))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        experiments = [experiment.to_dict() for experiment in pagination.items]
        
        return jsonify({
            'experiments': experiments,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@experiments_bp.route('/<int:experiment_id>', methods=['GET'])
@jwt_required()
def get_experiment(experiment_id):
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'message': '实验不存在'}), 404
        
        # TODO: 权限检查
        
        # 获取实验步骤和数据点
        steps = [step.to_dict() for step in experiment.steps]
        data_points = [dp.to_dict() for dp in experiment.data_points]
        
        experiment_data = experiment.to_dict()
        experiment_data['steps'] = steps
        experiment_data['data_points'] = data_points
        
        return jsonify({'experiment': experiment_data}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@experiments_bp.route('/', methods=['POST'])
@jwt_required()
@teacher_required
def create_experiment():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        instructions = data.get('instructions', '')
        objectives = data.get('objectives', '')
        requirements = data.get('requirements', '')
        max_score = data.get('max_score', 100.0)
        course_id = data.get('course_id')
        
        if not title or not course_id:
            return jsonify({'message': '实验标题和课程ID不能为空'}), 400
        
        # 检查课程权限
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        if current_user.role != 'admin' and course.teacher_id != current_user_id:
            return jsonify({'message': '只能在自己的课程中创建实验'}), 403
        
        experiment = Experiment(
            title=title,
            description=description,
            instructions=instructions,
            objectives=objectives,
            requirements=requirements,
            max_score=max_score,
            course_id=course_id
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify({
            'message': '实验创建成功',
            'experiment': experiment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@experiments_bp.route('/<int:experiment_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_experiment(experiment_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'message': '实验不存在'}), 404
        
        # 检查权限
        if current_user.role != 'admin' and experiment.course.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            experiment.title = data['title']
        if 'description' in data:
            experiment.description = data['description']
        if 'instructions' in data:
            experiment.instructions = data['instructions']
        if 'objectives' in data:
            experiment.objectives = data['objectives']
        if 'requirements' in data:
            experiment.requirements = data['requirements']
        if 'max_score' in data:
            experiment.max_score = data['max_score']
        if 'status' in data:
            experiment.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': '实验更新成功',
            'experiment': experiment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@experiments_bp.route('/<int:experiment_id>/steps', methods=['POST'])
@jwt_required()
@teacher_required
def add_experiment_step(experiment_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'message': '实验不存在'}), 404
        
        # 检查权限
        if current_user.role != 'admin' and experiment.course.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        expected_result = data.get('expected_result', '')
        scoring_criteria = data.get('scoring_criteria', '')
        order = data.get('order', 1)
        
        if not title:
            return jsonify({'message': '步骤标题不能为空'}), 400
        
        step = ExperimentStep(
            experiment_id=experiment_id,
            title=title,
            description=description,
            expected_result=expected_result,
            scoring_criteria=scoring_criteria,
            order=order
        )
        
        db.session.add(step)
        db.session.commit()
        
        return jsonify({
            'message': '实验步骤添加成功',
            'step': step.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@experiments_bp.route('/<int:experiment_id>/data-points', methods=['POST'])
@jwt_required()
@teacher_required
def add_data_point(experiment_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'message': '实验不存在'}), 404
        
        # 检查权限
        if current_user.role != 'admin' and experiment.course.teacher_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        name = data.get('name')
        type_value = data.get('type')
        unit = data.get('unit', '')
        is_required = data.get('is_required', False)
        value_range = data.get('value_range', '')
        options = data.get('options', '')
        
        if not name or not type_value:
            return jsonify({'message': '数据点名称和类型不能为空'}), 400
        
        data_point = DataPoint(
            experiment_id=experiment_id,
            name=name,
            type=type_value,
            unit=unit,
            is_required=is_required,
            value_range=value_range,
            options=options
        )
        
        db.session.add(data_point)
        db.session.commit()
        
        return jsonify({
            'message': '数据点添加成功',
            'data_point': data_point.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500