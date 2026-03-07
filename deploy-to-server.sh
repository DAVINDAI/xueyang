#!/bin/bash

set -e

echo "========================================="
echo "远程部署脚本"
echo "========================================="

SERVER="root@47.110.67.241"
SERVER_DIR="/opt/xueyang"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

upload_deployment_script() {
    echo "上传部署脚本到服务器..."
    scp "${LOCAL_DIR}/server-deploy.sh" "${SERVER}:${SERVER_DIR}/"
    ssh "${SERVER}" "chmod +x ${SERVER_DIR}/server-deploy.sh"
    echo "✓ 部署脚本上传完成"
}

upload_env_file() {
    echo "检查 .env 文件..."
    
    if [ ! -f "${LOCAL_DIR}/.env" ]; then
        echo "错误: 本地 .env 文件不存在"
        echo "请先创建 .env 文件并配置正确的环境变量"
        exit 1
    fi
    
    echo "上传 .env 文件到服务器..."
    scp "${LOCAL_DIR}/.env" "${SERVER}:${SERVER_DIR}/.env"
    echo "✓ .env 文件上传完成"
}

upload_docker_compose() {
    echo "上传 docker-compose.prod.yml 到服务器..."
    
    if [ ! -f "${LOCAL_DIR}/docker-compose.prod.yml" ]; then
        echo "错误: docker-compose.prod.yml 文件不存在"
        exit 1
    fi
    
    scp "${LOCAL_DIR}/docker-compose.prod.yml" "${SERVER}:${SERVER_DIR}/docker-compose.prod.yml"
    echo "✓ docker-compose.prod.yml 上传完成"
}

execute_deployment() {
    echo "在服务器上执行部署..."
    
    # 传递 DOCKER_REGISTRY_PASSWORD 环境变量
    if [ -n "${DOCKER_REGISTRY_PASSWORD}" ]; then
        ssh "${SERVER}" "cd ${SERVER_DIR} && DOCKER_REGISTRY_PASSWORD='${DOCKER_REGISTRY_PASSWORD}' ./server-deploy.sh"
    else
        ssh "${SERVER}" "cd ${SERVER_DIR} && ./server-deploy.sh"
    fi
}

main() {
    upload_deployment_script
    upload_env_file
    upload_docker_compose
    execute_deployment
}

main "$@"
