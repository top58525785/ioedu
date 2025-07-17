from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ioedu.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    # 初始化扩展
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.courses import courses_bp
    from routes.experiments import experiments_bp
    from routes.classes import classes_bp
    from routes.submissions import submissions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(experiments_bp, url_prefix='/api/experiments')
    app.register_blueprint(classes_bp, url_prefix='/api/classes')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 创建默认管理员用户
        from models.user import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@ioedu.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
    
    return app

# 全局数据库和序列化对象
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)