#!/bin/bash

set -e

echo "========================================="
echo "服务器部署脚本"
echo "========================================="

PROJECT_DIR="/opt/xueyang"
BACKUP_DIR="/opt/backups"
DOCKER_REGISTRY="crpi-76fbd77t4270ljs4-vpc.cn-hangzhou.personal.cr.aliyuncs.com"
DOCKER_USERNAME="davindai@hotmail.com"

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "错误: Docker Compose 未安装"
        exit 1
    fi
    
    echo "✓ Docker 和 Docker Compose 已安装"
}

docker_login() {
    echo "检查 Docker 登录状态..."
    
    if docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
        echo "✓ 已登录 Docker 仓库"
        return 0
    fi
    
    echo "未登录 Docker 仓库，尝试自动登录..."
    
    # 优先从环境变量读取密码
    if [ -n "${DOCKER_REGISTRY_PASSWORD}" ]; then
        echo "${DOCKER_REGISTRY_PASSWORD}" | docker login --username="${DOCKER_USERNAME}" --password-stdin "${DOCKER_REGISTRY}"
    # 其次从配置文件读取
    elif [ -f "${PROJECT_DIR}/.env" ] && grep -q "DOCKER_REGISTRY_PASSWORD" "${PROJECT_DIR}/.env"; then
        DOCKER_PASSWORD=$(grep "DOCKER_REGISTRY_PASSWORD" "${PROJECT_DIR}/.env" | cut -d'=' -f2)
        echo "${DOCKER_PASSWORD}" | docker login --username="${DOCKER_USERNAME}" --password-stdin "${DOCKER_REGISTRY}"
    else
        echo "错误: 未找到 Docker 登录密码"
        echo "请设置环境变量 DOCKER_REGISTRY_PASSWORD 或在 ${PROJECT_DIR}/.env 文件中配置"
        exit 1
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Docker 登录失败"
        exit 1
    fi
    
    echo "✓ Docker 登录成功"
}

check_env_file() {
    if [ ! -f "${PROJECT_DIR}/.env" ]; then
        echo "错误: .env 文件不存在: ${PROJECT_DIR}/.env"
        exit 1
    fi
    
    if grep -q "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION" "${PROJECT_DIR}/.env"; then
        echo "警告: SECRET_KEY 仍然是默认值，请修改为安全的随机字符串"
        read -p "是否继续部署? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo "✓ .env 文件已配置"
}

pull_images() {
    echo "正在拉取最新镜像..."
    
    cd "${PROJECT_DIR}"
    
    # 拉取后端镜像
    echo "拉取后端镜像..."
    docker pull "${DOCKER_REGISTRY}/xueyang_me/backend:latest"
    
    # 拉取前端镜像
    echo "拉取前端镜像..."
    docker pull "${DOCKER_REGISTRY}/xueyang_me/frontend:latest"
    
    echo "✓ 镜像拉取完成"
}

backup_data() {
    if [ -d "${PROJECT_DIR}/data" ] || [ -d "${PROJECT_DIR}/results" ]; then
        echo "正在备份数据..."
        mkdir -p $BACKUP_DIR
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $PROJECT_DIR data results 2>/dev/null || true
        echo "✓ 数据备份完成: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    fi
}

deploy_services() {
    echo "正在部署服务..."
    
    cd "${PROJECT_DIR}"
    
    # 停止旧服务
    echo "停止旧服务..."
    docker compose -f docker-compose.prod.yml down || true
    
    # 启动新服务
    echo "启动新服务..."
    docker compose -f docker-compose.prod.yml up -d
    
    echo "✓ 服务部署完成"
}

check_health() {
    echo "等待服务启动..."
    sleep 10
    
    echo "检查服务健康状态..."
    docker compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "检查后端服务..."
    if curl -f http://localhost:80/docs &> /dev/null; then
        echo "✓ 后端服务正常"
    else
        echo "⚠ 后端服务可能未正常启动，请检查日志"
    fi
    
    echo ""
    echo "检查前端服务..."
    if curl -f http://localhost:80 &> /dev/null; then
        echo "✓ 前端服务正常"
    else
        echo "⚠ 前端服务可能未正常启动，请检查日志"
    fi
    
    # 清理历史镜像，释放磁盘空间
    echo ""
    echo "正在清理未使用的旧镜像..."
    docker image prune -af 2>/dev/null || echo "镜像清理完成"
    echo "✓ 旧镜像清理完成"
}

show_logs() {
    echo ""
    echo "========================================="
    echo "部署完成！"
    echo "========================================="
    echo ""
    echo "访问地址:"
    echo "  前端: http://47.110.67.241"
    echo "  后端: http://47.110.67.241/api"
    echo "  API文档: http://47.110.67.241/docs"
    echo "  OpenAPI: http://47.110.67.241/openapi.json"
    echo "  ReDoc: http://47.110.67.241/redoc"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker compose -f ${PROJECT_DIR}/docker-compose.prod.yml logs -f"
    echo "  停止服务: docker compose -f ${PROJECT_DIR}/docker-compose.prod.yml down"
    echo "  重启服务: docker compose -f ${PROJECT_DIR}/docker-compose.prod.yml restart"
    echo ""
}

main() {
    check_docker
    docker_login
    check_env_file
    pull_images
    backup_data
    deploy_services
    check_health
    show_logs
}

main "$@"
