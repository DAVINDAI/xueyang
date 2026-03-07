#!/bin/bash

# Docker 镜像构建脚本

# 设置镜像名称和标签
IMAGE_NAME="crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend"
IMAGE_TAG="${1:-latest}"
DOCKER_REGISTRY="crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com"
DOCKER_USERNAME="davindai@hotmail.com"

# 检查登录状态并自动登录
check_and_login() {
    if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
        echo "未登录 Docker 仓库，尝试自动登录..."
        
        # 优先从环境变量读取密码
        if [ -n "${DOCKER_REGISTRY_PASSWORD}" ]; then
            echo "${DOCKER_REGISTRY_PASSWORD}" | docker login --username="${DOCKER_USERNAME}" --password-stdin "${DOCKER_REGISTRY}"
        # 其次从 .env 文件读取
        elif [ -f .env ] && grep -q "DOCKER_REGISTRY_PASSWORD" .env; then
            DOCKER_PASSWORD=$(grep "DOCKER_REGISTRY_PASSWORD" .env | cut -d'=' -f2)
            echo "${DOCKER_PASSWORD}" | docker login --username="${DOCKER_USERNAME}" --password-stdin "${DOCKER_REGISTRY}"
        else
            echo "错误: 未找到 Docker 登录密码"
            echo "请设置环境变量 DOCKER_REGISTRY_PASSWORD 或在 .env 文件中配置"
            exit 1
        fi
        
        if [ $? -ne 0 ]; then
            echo "❌ Docker 登录失败"
            exit 1
        fi
        echo "✅ Docker 登录成功"
    else
        echo "✅ 已登录 Docker 仓库"
    fi
}

# 构建镜像
echo "开始构建 Docker 镜像..."
echo "镜像名称: ${IMAGE_NAME}"
echo "镜像标签: ${IMAGE_TAG}"

docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if [ $? -eq 0 ]; then
    echo "✅ Docker 镜像构建成功: ${IMAGE_NAME}:${IMAGE_TAG}"
    
    # 询问是否推送到阿里云
    read -p "是否推送到阿里云仓库? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        check_and_login
        echo "正在推送镜像..."
        docker push "${IMAGE_NAME}:${IMAGE_TAG}"
        if [ $? -eq 0 ]; then
            echo "✅ 镜像推送成功"
        else
            echo "❌ 镜像推送失败"
            exit 1
        fi
    fi
else
    echo "❌ Docker 镜像构建失败"
    exit 1
fi