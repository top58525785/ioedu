#!/bin/bash

# 高校在线实验管理系统启动脚本
echo "🚀 启动高校在线实验管理系统..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端服务
echo "📡 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🔥 启动Flask后端 (http://localhost:5000)..."
python3 app.py &
BACKEND_PID=$!

cd ..

# 启动前端服务
echo "⚛️ 启动前端服务..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装npm依赖..."
    npm install
fi

echo "🌐 启动React前端 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ 系统启动完成!"
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:5000"
echo "👤 默认管理员账户: admin / admin123"
echo ""
echo "按 Ctrl+C 停止所有服务..."

# 等待用户中断
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 保持脚本运行
wait