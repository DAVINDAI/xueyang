#!/bin/bash

# Docker 镜像分层构建脚本

IMAGE_NAME="crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend"
IMAGE_TAG="${1:-latest}"
DOCKER_REGISTRY="crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com"
DOCKER_USERNAME="davindai@hotmail.com"

# 检查登录状态并自动登录
check_and_login() {
    if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
        echo "未登录 Docker 仓库，尝试自动登录..."
        
        if [ -n "${DOCKER_REGISTRY_PASSWORD}" ]; then
            echo "${DOCKER_REGISTRY_PASSWORD}" | docker login --username="${DOCKER_USERNAME}" --password-stdin "${DOCKER_REGISTRY}"
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

# 构建并推送 base 镜像
build_base() {
    echo "========================================="
    echo "构建 base 镜像（系统依赖）"
    echo "========================================="
    
    docker build --target base -t "${IMAGE_NAME}:base" .
    
    if [ $? -eq 0 ]; then
        echo "✅ base 镜像构建成功"
    else
        echo "❌ base 镜像构建失败"
        exit 1
    fi
}

# 构建并推送 deps 镜像
build_deps() {
    echo "========================================="
    echo "构建 deps 镜像（Python 依赖）"
    echo "========================================="
    
    docker build --target deps -t "${IMAGE_NAME}:deps" .
    
    if [ $? -eq 0 ]; then
        echo "✅ deps 镜像构建成功"
    else
        echo "❌ deps 镜像构建失败"
        exit 1
    fi
}

# 构建并推送 final 镜像
build_final() {
    echo "========================================="
    echo "构建 final 镜像（应用代码）"
    echo "========================================="
    
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
    
    if [ $? -eq 0 ]; then
        echo "✅ final 镜像构建成功: ${IMAGE_NAME}:${IMAGE_TAG}"
    else
        echo "❌ final 镜像构建失败"
        exit 1
    fi
}

# 推送镜像
push_image() {
    local image_tag=$1
    echo "正在推送镜像: ${image_tag}"
    docker push "${IMAGE_NAME}:${image_tag}"
    
    if [ $? -eq 0 ]; then
        echo "✅ 镜像推送成功: ${image_tag}"
    else
        echo "❌ 镜像推送失败: ${image_tag}"
        exit 1
    fi
}

# 检查镜像是否存在
check_image_exists() {
    local image_tag=$1
    if docker image inspect "${IMAGE_NAME}:${image_tag}" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 主流程
main() {
    echo "开始分层构建..."
    echo "镜像名称: ${IMAGE_NAME}"
    echo "镜像标签: ${IMAGE_TAG}"
    echo ""
    
    # 检查 base 镜像
    if check_image_exists "base"; then
        echo "base 镜像已存在，跳过构建"
    else
        build_base
        check_and_login
        push_image "base"
    fi
    
    echo ""
    
    # 检查 deps 镜像
    if check_image_exists "deps"; then
        echo "deps 镜像已存在，跳过构建"
    else
        build_deps
        check_and_login
        push_image "deps"
    fi
    
    echo ""
    
    # 总是构建 final 镜像
    build_final
    
    echo ""
    read -p "是否推送到阿里云仓库? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        check_and_login
        push_image "${IMAGE_TAG}"
    fi
    
    echo ""
    echo "========================================="
    echo "构建完成！"
    echo "========================================="
    echo ""
    echo "镜像列表："
    echo "  - ${IMAGE_NAME}:base"
    echo "  - ${IMAGE_NAME}:deps"
    echo "  - ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
}

main "$@"
