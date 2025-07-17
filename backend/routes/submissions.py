from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models.user import User
from models.experiment import Experiment
from models.submission import Submission
from utils.decorators import teacher_required

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/', methods=['GET'])
@jwt_required()
def get_submissions():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        experiment_id = request.args.get('experiment_id', type=int)
        student_id = request.args.get('student_id', type=int)
        status = request.args.get('status')
        
        query = Submission.query
        
        # 学生只能看到自己的提交
        if current_user.role == 'student':
            query = query.filter(Submission.student_id == current_user_id)
        elif current_user.role == 'teacher':
            # 教师只能看到自己课程实验的提交
            # TODO: 根据教师的课程过滤
            pass
        
        if experiment_id:
            query = query.filter(Submission.experiment_id == experiment_id)
        
        if student_id and current_user.role in ['admin', 'teacher']:
            query = query.filter(Submission.student_id == student_id)
        
        if status:
            query = query.filter(Submission.status == status)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        submissions = [submission.to_dict() for submission in pagination.items]
        
        return jsonify({
            'submissions': submissions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        submission = Submission.query.get(submission_id)
        if not submission:
            return jsonify({'message': '提交不存在'}), 404
        
        # 权限检查：学生只能看自己的提交，教师可以看自己课程的提交
        if current_user.role == 'student' and submission.student_id != current_user_id:
            return jsonify({'message': '权限不足'}), 403
        elif current_user.role == 'teacher':
            # TODO: 检查是否是教师的课程
            pass
        
        return jsonify({'submission': submission.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/', methods=['POST'])
@jwt_required()
def create_submission():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'student':
            return jsonify({'message': '只有学生可以提交实验'}), 403
        
        data = request.get_json()
        experiment_id = data.get('experiment_id')
        content = data.get('content', '')
        data_values = data.get('data_values', '')
        files = data.get('files', '')
        
        if not experiment_id:
            return jsonify({'message': '实验ID不能为空'}), 400
        
        # 检查实验是否存在
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'message': '实验不存在'}), 404
        
        # 检查是否有权限提交（TODO: 检查实验分配）
        
        # 获取当前提交次数
        existing_submissions = Submission.query.filter_by(
            experiment_id=experiment_id,
            student_id=current_user_id
        ).count()
        
        attempt_number = existing_submissions + 1
        
        submission = Submission(
            experiment_id=experiment_id,
            student_id=current_user_id,
            attempt_number=attempt_number,
            content=content,
            data_values=data_values,
            files=files,
            status='draft'
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'message': '实验提交创建成功',
            'submission': submission.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/<int:submission_id>', methods=['PUT'])
@jwt_required()
def update_submission(submission_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        submission = Submission.query.get(submission_id)
        if not submission:
            return jsonify({'message': '提交不存在'}), 404
        
        # 学生只能修改自己的提交
        if current_user.role == 'student':
            if submission.student_id != current_user_id:
                return jsonify({'message': '权限不足'}), 403
            
            # 已批改的提交不能修改
            if submission.status == 'graded':
                return jsonify({'message': '已批改的提交不能修改'}), 400
        
        data = request.get_json()
        
        # 学生更新提交内容
        if current_user.role == 'student':
            if 'content' in data:
                submission.content = data['content']
            if 'data_values' in data:
                submission.data_values = data['data_values']
            if 'files' in data:
                submission.files = data['files']
            if 'status' in data and data['status'] in ['draft', 'submitted']:
                submission.status = data['status']
                if data['status'] == 'submitted':
                    submission.submitted_at = datetime.utcnow()
        
        # 教师批改
        elif current_user.role in ['admin', 'teacher']:
            if 'score' in data:
                submission.score = data['score']
            if 'feedback' in data:
                submission.feedback = data['feedback']
            if 'status' in data and data['status'] == 'graded':
                submission.status = 'graded'
                submission.graded_by = current_user_id
                submission.graded_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '提交更新成功',
            'submission': submission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/<int:submission_id>/grade', methods=['POST'])
@jwt_required()
@teacher_required
def grade_submission(submission_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        submission = Submission.query.get(submission_id)
        if not submission:
            return jsonify({'message': '提交不存在'}), 404
        
        # 检查权限：TODO 检查是否是教师的课程
        
        data = request.get_json()
        score = data.get('score')
        feedback = data.get('feedback', '')
        
        if score is None:
            return jsonify({'message': '分数不能为空'}), 400
        
        submission.score = score
        submission.feedback = feedback
        submission.status = 'graded'
        submission.graded_by = current_user_id
        submission.graded_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '批改完成',
            'submission': submission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500