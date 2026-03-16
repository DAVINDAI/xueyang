#!/bin/bash

set -e

echo "========================================="
echo "生产环境部署脚本"
echo "========================================="

PROJECT_DIR="/opt/xueyang"
BACKUP_DIR="/opt/backups"

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker 未安装"
        echo "请先安装 Docker: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker Compose 未安装"
        echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo "✓ Docker 和 Docker Compose 已安装"
}

check_env_file() {
    if [ ! -f ".env" ]; then
        echo "错误: .env 文件不存在"
        echo "请复制 .env.production.example 为 .env 并配置正确的环境变量"
        exit 1
    fi
    
    if grep -q "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION" .env; then
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
    docker compose -f docker-compose.prod.yml pull
    echo "✓ 镜像拉取完成"
}

backup_data() {
    if [ -d "$PROJECT_DIR/data" ]; then
        echo "正在备份数据..."
        mkdir -p $BACKUP_DIR
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $PROJECT_DIR data results 2>/dev/null || true
        echo "✓ 数据备份完成: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    fi
}

deploy_services() {
    echo "正在部署服务..."
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
    if curl -f http://localhost:8000/docs &> /dev/null; then
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
}

show_logs() {
    echo ""
    echo "========================================="
    echo "部署完成！"
    echo "========================================="
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker compose -f docker-compose.prod.yml logs -f"
    echo "  停止服务: docker compose -f docker-compose.prod.yml down"
    echo "  重启服务: docker compose -f docker-compose.prod.yml restart"
    echo ""
}

main() {
    check_docker
    check_env_file
    pull_images
    backup_data
    deploy_services
    check_health
    show_logs
}

main "$@"
