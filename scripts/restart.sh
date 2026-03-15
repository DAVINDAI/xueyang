#!/bin/bash

# 学氧助手 - 本地开发环境重启脚本
# 先停止服务，然后重新启动

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# PID 文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  学氧助手 - 重启服务${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# 步骤1: 停止服务
echo -e "${YELLOW}步骤 1/2: 停止服务...${NC}"

# 调用 stop.sh 停止服务
if [ -f "$PROJECT_ROOT/scripts/stop.sh" ]; then
    bash "$PROJECT_ROOT/scripts/stop.sh"
else
    echo -e "${RED}错误: 未找到 stop.sh 脚本${NC}"
    # 清理可能存在的 PID 文件
    if [ -f "$BACKEND_PID_FILE" ]; then
        rm -f "$BACKEND_PID_FILE"
    fi
    if [ -f "$FRONTEND_PID_FILE" ]; then
        rm -f "$FRONTEND_PID_FILE"
    fi
    echo -e "${YELLOW}已清理残留的 PID 文件${NC}"
    exit 1
fi

# 等待一下确保端口释放
sleep 2

echo ""
echo -e "${YELLOW}步骤 2/2: 启动服务...${NC}"

# 步骤2: 启动服务
if [ -f "$PROJECT_ROOT/scripts/start.sh" ]; then
    bash "$PROJECT_ROOT/scripts/start.sh"
else
    echo -e "${RED}错误: 未找到 start.sh 脚本${NC}"
    # 清理可能存在的 PID 文件
    if [ -f "$BACKEND_PID_FILE" ]; then
        rm -f "$BACKEND_PID_FILE"
    fi
    if [ -f "$FRONTEND_PID_FILE" ]; then
        rm -f "$FRONTEND_PID_FILE"
    fi
    echo -e "${YELLOW}已清理残留的 PID 文件${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  服务重启完成！${NC}"
echo -e "${GREEN}=========================================${NC}"