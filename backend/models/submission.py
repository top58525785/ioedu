from app import db, ma
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attempt_number = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, graded
    content = db.Column(db.Text)  # JSON string
    data_values = db.Column(db.Text)  # JSON string for data points
    files = db.Column(db.Text)  # JSON string for file paths
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    graded_at = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    grader = db.relationship('User', foreign_keys=[graded_by], backref='graded_submissions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'experiment_title': self.experiment.title if self.experiment else None,
            'student_id': self.student_id,
            'student_name': self.student.username if self.student else None,
            'attempt_number': self.attempt_number,
            'status': self.status,
            'content': self.content,
            'data_values': self.data_values,
            'files': self.files,
            'score': self.score,
            'feedback': self.feedback,
            'graded_by': self.graded_by,
            'grader_name': self.grader.username if self.grader else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Submission
        load_instance = True
        include_fk = True