from app import db, ma
from datetime import datetime

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    student_enrollments = db.relationship('StudentClass', backref='class_obj', lazy=True)
    course_associations = db.relationship('ClassCourse', backref='class_obj', lazy=True)
    assignments = db.relationship('ExperimentAssignment', backref='assigned_class', lazy=True, 
                                foreign_keys='ExperimentAssignment.assignee_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None,
            'student_count': len(self.student_enrollments),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StudentClass(db.Model):
    __tablename__ = 'student_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('student_id', 'class_id', name='unique_student_class'),)
    
    student = db.relationship('User', backref='class_enrollments')

class ClassCourse(db.Model):
    __tablename__ = 'class_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('class_id', 'course_id', name='unique_class_course'),)

class ClassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Class
        load_instance = True
        include_fk = True

class StudentClassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StudentClass
        load_instance = True
        include_fk = True