#!/bin/bash

set -e

echo "========================================="
echo "停止生产环境服务"
echo "========================================="

echo "正在停止服务..."
docker compose -f docker-compose.prod.yml down

echo ""
echo "✓ 服务已停止"
echo ""
echo "如需重新启动，请运行: ./deploy.sh"
