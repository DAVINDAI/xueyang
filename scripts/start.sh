#!/bin/bash

# 学氧助手项目启动脚本
# 同时启动后端和前端服务，并支持热重载

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID 文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# 日志文件
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志轮转函数
rotate_log() {
    local log_file=$1
    local max_size=10485760  # 10MB
    
    if [ -f "$log_file" ]; then
        local file_size=$(wc -c <"$log_file")
        if [ "$file_size" -gt "$max_size" ]; then
            local timestamp=$(date +"%Y%m%d_%H%M%S")
            local backup_file="${log_file%.log}_${timestamp}.log"
            mv "$log_file" "$backup_file"
            echo -e "${YELLOW}日志已轮转: $backup_file${NC}"
        fi
    fi
}

# 清理函数
cleanup() {
    echo -e "${YELLOW}\n正在停止服务...${NC}"
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE" 2>/dev/null || true)
        if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill "$BACKEND_PID" 2>/dev/null || true
            echo -e "${RED}后端服务已停止${NC}"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE" 2>/dev/null || true)
        if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID" 2>/dev/null || true
            echo -e "${RED}前端服务已停止${NC}"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
}

# 信号处理
trap cleanup EXIT INT TERM

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}端口 $port 已被占用${NC}"
        return 1
    fi
    return 0
}

# 启动后端服务
start_backend() {
    echo -e "${BLUE}正在启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    # 日志轮转
    rotate_log "$BACKEND_LOG"
    
    # 生成SECRET_KEY（如果不存在）
    if [ -z "$SECRET_KEY" ]; then
        export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo -e "${GREEN}已生成SECRET_KEY: $SECRET_KEY${NC}"
    else
        echo -e "${GREEN}使用现有的SECRET_KEY${NC}"
    fi
    
    # 检查虚拟环境（先检查项目根目录，再检查backend目录）
    if [ -d "$PROJECT_ROOT/venv" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        echo -e "${GREEN}已激活虚拟环境: $PROJECT_ROOT/venv${NC}"
    elif [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}已激活虚拟环境: venv${NC}"
    fi
    
    # 检查依赖
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}正在安装后端依赖...${NC}"
        pip3 install -r requirements.txt
    fi
    
    # 启动后端 (使用 uvicorn 的 --reload 选项支持热重载，使用 >> 追加模式)
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload >> "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    # 等待后端启动
    sleep 3
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
        echo -e "${BLUE}后端地址: http://localhost:8000${NC}"
        echo -e "${BLUE}API 文档: http://localhost:8000/docs${NC}"
        echo -e "${BLUE}后端日志: $BACKEND_LOG${NC}"
    else
        echo -e "${RED}后端服务启动失败${NC}"
        tail -n 20 "$BACKEND_LOG"
        exit 1
    fi
}

# 启动前端服务
start_frontend() {
    echo -e "${BLUE}\n正在启动前端服务...${NC}"
    cd "$FRONTEND_DIR"
    
    # 日志轮转
    rotate_log "$FRONTEND_LOG"
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装前端依赖...${NC}"
        npm install
    fi

    # 启动前端 (Vite 默认支持热重载，使用 >> 追加模式)
    VITE_API_BASE_URL=http://localhost:8000/api nohup npm run dev >> "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    # 等待前端启动
    sleep 4
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"
        echo -e "${BLUE}前端地址: http://localhost:5173${NC}"
        echo -e "${BLUE}前端日志: $FRONTEND_LOG${NC}"
    else
        echo -e "${RED}前端服务启动失败${NC}"
        tail -n 20 "$FRONTEND_LOG"
        exit 1
    fi
}

# 主函数
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  学氧助手项目启动脚本${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # 检查端口
    check_port 8000 || exit 1
    check_port 5173 || exit 1
    
    # 启动服务
    start_backend
    start_frontend
    
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  所有服务已启动完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${YELLOW}\n按 Ctrl+C 停止所有服务${NC}"
    echo -e "${YELLOW}查看日志:${NC}"
    echo -e "  后端: tail -f $BACKEND_LOG"
    echo -e "  前端: tail -f $FRONTEND_LOG"
    
    # 保持脚本运行
    wait
}

# 运行主函数
main
