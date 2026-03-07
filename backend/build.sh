#!/bin/bash

# Docker 镜像构建脚本

# 设置镜像名称和标签
IMAGE_NAME="crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend"
IMAGE_TAG="${1:-latest}"

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