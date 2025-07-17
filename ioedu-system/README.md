# 高校在线实验管理系统 (IOEdu)

一个现代化的高校实验教学管理平台，支持多角色用户管理、课程管理、实验管理、班级管理和实验提交评分等功能。

## 功能特性

### 用户角色
- **管理员**: 系统全局管理、用户管理、权限分配
- **教师**: 课程与实验管理、学生指导、成绩评定
- **学生**: 参与实验学习、提交作业、查看成绩

### 核心功能
- 📚 **课程管理**: 创建、编辑、管理实验课程
- 🔬 **实验管理**: 结构化实验设计，支持步骤化流程和数据点定义
- 👥 **班级管理**: 班级创建、学生管理、课程分配
- 📝 **实验提交**: 支持多次提交、在线批改、成绩反馈
- 📊 **数据统计**: 实验完成率、成绩分析、教学效果评估

## 技术栈

### 前端
- **React 18** - 现代化UI框架
- **TypeScript** - 类型安全
- **Vite** - 快速构建工具
- **Tailwind CSS** - 现代化样式框架
- **Lucide Icons** - 图标库
- **Zustand** - 状态管理
- **Axios** - HTTP客户端
- **React Router** - 路由管理

### 后端
- **Flask 3.x** - 轻量级Web框架
- **SQLAlchemy 2.x** - ORM框架
- **SQLite** - 数据库(可扩展为PostgreSQL/MySQL)
- **Flask-JWT-Extended** - JWT认证
- **Flask-CORS** - 跨域支持
- **Marshmallow** - 数据序列化与验证

## 快速开始

### 系统要求
- Node.js 18+ 
- Python 3.8+
- Git

### 安装与运行

#### 1. 克隆项目
```bash
git clone <repository-url>
cd ioedu-system
```

#### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
python3 app.py
```
后端服务将在 http://localhost:5000 启动

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```
前端服务将在 http://localhost:5173 启动

### 默认账户
- **管理员**: admin / admin123
- 首次登录后请修改默认密码

## 项目结构

```
ioedu-system/
├── backend/                 # Flask后端
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   ├── utils/              # 工具函数
│   ├── app.py              # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── store/          # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── utils/          # 工具函数
│   ├── package.json        # 依赖配置
│   └── vite.config.ts      # 构建配置
└── README.md               # 项目说明
```

## API 文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/change-password` - 修改密码

### 用户管理接口
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `PUT /api/users/{id}` - 更新用户
- `DELETE /api/users/{id}` - 删除用户

### 课程管理接口
- `GET /api/courses` - 获取课程列表
- `POST /api/courses` - 创建课程
- `PUT /api/courses/{id}` - 更新课程
- `DELETE /api/courses/{id}` - 删除课程

### 实验管理接口
- `GET /api/experiments` - 获取实验列表
- `POST /api/experiments` - 创建实验
- `PUT /api/experiments/{id}` - 更新实验
- `POST /api/experiments/{id}/steps` - 添加实验步骤
- `POST /api/experiments/{id}/data-points` - 添加数据点

## 部署

### 开发环境
使用上述快速开始步骤即可

### 生产环境
1. 配置生产数据库(PostgreSQL/MySQL)
2. 设置环境变量(JWT密钥、数据库连接等)
3. 构建前端静态文件: `npm run build`
4. 使用Nginx代理后端API和前端静态文件
5. 使用Gunicorn或uWSGI运行Flask应用

## 开发计划

### Phase 1: 基础功能 ✅
- [x] 用户认证与权限管理
- [x] 基础的课程管理
- [x] 简单的实验创建与查看
- [x] 基本的班级管理

### Phase 2: 核心功能 🚧
- [ ] 完整的实验管理(包括步骤和数据点)
- [ ] 实验分配机制
- [ ] 基础的提交与批改功能
- [ ] 简单的数据统计

### Phase 3: 高级功能 📋
- [ ] 高级批改功能
- [ ] 详细的数据分析与报表
- [ ] 系统优化与性能提升
- [ ] 用户体验优化

## 贡献

欢迎提交Issue和Pull Request!

## 许可证

MIT License