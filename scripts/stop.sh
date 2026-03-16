#!/bin/bash

# 学氧助手 - 本地开发环境停止脚本
# 停止本地后端和前端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  学氧助手 - 停止服务${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# 检查是否有 PID 文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

if [ -f "$BACKEND_PID_FILE" ] || [ -f "$FRONTEND_PID_FILE" ]; then
    echo "发现 PID 文件，正在停止本地服务..."
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE" 2>/dev/null || true)
        if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill "$BACKEND_PID" 2>/dev/null || true
            echo -e "${GREEN}✓ 后端服务已停止${NC}"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE" 2>/dev/null || true)
        if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID" 2>/dev/null || true
            echo -e "${GREEN}✓ 前端服务已停止${NC}"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
else
    echo "未找到 PID 文件，服务可能未运行"
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  服务已停止！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "如需重新启动，请运行: ${BLUE}bash scripts/restart.sh${NC}"