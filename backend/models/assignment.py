from app import db, ma
from datetime import datetime

class ExperimentAssignment(db.Model):
    __tablename__ = 'experiment_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    assignee_type = db.Column(db.String(20), nullable=False)  # 'class' or 'student'
    assignee_id = db.Column(db.Integer, nullable=False)  # class_id or student_id
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    max_attempts = db.Column(db.Integer, default=3)
    status = db.Column(db.String(20), default='assigned')  # assigned, active, completed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        assignee_name = None
        if self.assignee_type == 'class':
            from models.class_model import Class
            class_obj = Class.query.get(self.assignee_id)
            assignee_name = class_obj.name if class_obj else None
        elif self.assignee_type == 'student':
            from models.user import User
            student = User.query.get(self.assignee_id)
            assignee_name = student.username if student else None
            
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'experiment_title': self.experiment.title if self.experiment else None,
            'assignee_type': self.assignee_type,
            'assignee_id': self.assignee_id,
            'assignee_name': assignee_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'max_attempts': self.max_attempts,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class ExperimentAssignmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExperimentAssignment
        load_instance = True
        include_fk = True