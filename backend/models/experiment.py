from app import db, ma
from datetime import datetime

class Experiment(db.Model):
    __tablename__ = 'experiments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    objectives = db.Column(db.Text)
    requirements = db.Column(db.Text)
    max_score = db.Column(db.Float, default=100.0)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, published, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    steps = db.relationship('ExperimentStep', backref='experiment', lazy=True, cascade='all, delete-orphan')
    data_points = db.relationship('DataPoint', backref='experiment', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('ExperimentAssignment', backref='experiment', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='experiment', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'objectives': self.objectives,
            'requirements': self.requirements,
            'max_score': self.max_score,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'steps_count': len(self.steps),
            'data_points_count': len(self.data_points)
        }

class ExperimentStep(db.Model):
    __tablename__ = 'experiment_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    scoring_criteria = db.Column(db.Text)
    order = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'title': self.title,
            'description': self.description,
            'expected_result': self.expected_result,
            'scoring_criteria': self.scoring_criteria,
            'order': self.order,
            'created_at': self.created_at.isoformat()
        }

class DataPoint(db.Model):
    __tablename__ = 'data_points'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # number, text, select, file
    unit = db.Column(db.String(50))
    is_required = db.Column(db.Boolean, default=False)
    value_range = db.Column(db.String(200))
    options = db.Column(db.Text)  # JSON string for select type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'name': self.name,
            'type': self.type,
            'unit': self.unit,
            'is_required': self.is_required,
            'value_range': self.value_range,
            'options': self.options,
            'created_at': self.created_at.isoformat()
        }

class ExperimentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Experiment
        load_instance = True
        include_fk = True

class ExperimentStepSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExperimentStep
        load_instance = True
        include_fk = True

class DataPointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DataPoint
        load_instance = True
        include_fk = True