#!/bin/bash

# LangGraph 项目停止脚本
# 停止后端和前端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PID 文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# 停止进程函数
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null || true)
        if [ -n "$pid" ]; then
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
                # 等待进程结束
                for i in {1..10}; do
                    if ! kill -0 "$pid" 2>/dev/null; then
                        break
                    fi
                    sleep 0.5
                done
                # 如果还在运行，强制杀死
                if kill -0 "$pid" 2>/dev/null; then
                    kill -9 "$pid" 2>/dev/null || true
                fi
                echo -e "${GREEN}${service_name}服务已停止${NC}"
            else
                echo -e "${YELLOW}${service_name}服务进程不存在${NC}"
            fi
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}未找到${service_name}服务的 PID 文件${NC}"
    fi
}

# 主函数
main() {
    echo -e "${YELLOW}正在停止 LangGraph 项目服务...${NC}"
    echo ""
    
    stop_process "$BACKEND_PID_FILE" "后端"
    stop_process "$FRONTEND_PID_FILE" "前端"
    
    echo ""
    echo -e "${GREEN}所有服务已停止${NC}"
}

# 运行主函数
main
