#!/bin/bash

# 远程服务器部署脚本
# 服务器: 47.110.67.241
# 用户: root

set -e

echo "========================================="
echo "远程服务器部署脚本"
echo "服务器: 47.110.67.241"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Docker
echo -e "${YELLOW}步骤 1: 检查 Docker 环境${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker 未安装，正在安装...${NC}"
    curl -fsSL https://get.docker.com | bash
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✓ Docker 安装完成${NC}"
else
    echo -e "${GREEN}✓ Docker 已安装${NC}"
fi

# 步骤 2: 检查 Docker Compose
echo -e "${YELLOW}步骤 2: 检查 Docker Compose${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose 未安装${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker Compose 已安装${NC}"
fi

# 步骤 3: 创建项目目录
echo -e "${YELLOW}步骤 3: 创建项目目录${NC}"
mkdir -p /opt/xueyang
cd /opt/xueyang
echo -e "${GREEN}✓ 项目目录创建完成: /opt/xueyang${NC}"

# 步骤 4: 检查项目文件
echo -e "${YELLOW}步骤 4: 检查项目文件${NC}"
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}错误: 项目文件不存在${NC}"
    echo "请先上传项目文件到 /opt/xueyang 目录"
    echo ""
    echo "在本地机器上执行："
    echo "rsync -avz --exclude 'node_modules' --exclude '.git' \\"
    echo "  /Users/work/ai_project/xueyang/ root@47.110.67.241:/opt/xueyang/"
    exit 1
fi
echo -e "${GREEN}✓ 项目文件检查完成${NC}"

# 步骤 5: 检查环境变量
echo -e "${YELLOW}步骤 5: 检查环境变量${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请先创建 .env 文件："
    echo "  cp .env.production.example .env"
    echo "  nano .env"
    exit 1
fi

if grep -q "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION" .env; then
    echo -e "${RED}警告: SECRET_KEY 仍然是默认值！${NC}"
    echo "请修改 .env 文件中的 SECRET_KEY"
    echo "生成命令: openssl rand -hex 32"
    exit 1
fi
echo -e "${GREEN}✓ 环境变量检查完成${NC}"

# 步骤 6: 登录阿里云镜像仓库
echo -e "${YELLOW}步骤 6: 登录阿里云镜像仓库${NC}"
echo "请输入阿里云镜像仓库密码："
docker login --username=davindai@hotmail.com crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 镜像仓库登录成功${NC}"
else
    echo -e "${RED}镜像仓库登录失败${NC}"
    exit 1
fi

# 步骤 7: 拉取镜像
echo -e "${YELLOW}步骤 7: 拉取最新镜像${NC}"
docker compose -f docker-compose.prod.yml pull
echo -e "${GREEN}✓ 镜像拉取完成${NC}"

# 步骤 8: 停止旧服务（如果存在）
echo -e "${YELLOW}步骤 8: 停止旧服务${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
echo -e "${GREEN}✓ 旧服务已停止${NC}"

# 步骤 9: 启动服务
echo -e "${YELLOW}步骤 9: 启动服务${NC}"
docker compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✓ 服务启动完成${NC}"

# 步骤 10: 等待服务启动
echo -e "${YELLOW}步骤 10: 等待服务启动${NC}"
sleep 15

# 步骤 11: 检查服务状态
echo -e "${YELLOW}步骤 11: 检查服务状态${NC}"
docker compose -f docker-compose.prod.yml ps

# 步骤 12: 健康检查
echo -e "${YELLOW}步骤 12: 健康检查${NC}"
echo "检查后端服务..."
if curl -f http://localhost:8000/docs &> /dev/null; then
    echo -e "${GREEN}✓ 后端服务正常${NC}"
else
    echo -e "${RED}✗ 后端服务异常${NC}"
fi

echo "检查前端服务..."
if curl -f http://localhost:80 &> /dev/null; then
    echo -e "${GREEN}✓ 前端服务正常${NC}"
else
    echo -e "${RED}✗ 前端服务异常${NC}"
fi

# 步骤 13: 配置防火墙
echo -e "${YELLOW}步骤 13: 配置防火墙${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    echo -e "${GREEN}✓ 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠ UFW 未安装，请手动配置防火墙${NC}"
fi

# 完成
echo ""
echo "========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "========================================="
echo ""
echo "访问地址:"
echo "  前端: http://47.110.67.241"
echo "  后端: http://47.110.67.241:8000"
echo "  API文档: http://47.110.67.241:8000/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker compose -f docker-compose.prod.yml logs -f"
echo "  停止服务: docker compose -f docker-compose.prod.yml down"
echo "  重启服务: docker compose -f docker-compose.prod.yml restart"
echo ""
