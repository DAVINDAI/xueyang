#!/bin/bash

# 最小化部署 - 只上传必需文件

SERVER="root@47.110.67.241"
REMOTE_DIR="/opt/xueyang"

echo "========================================="
echo "上传必需文件到服务器"
echo "========================================="

# 创建远程目录
ssh $SERVER "mkdir -p $REMOTE_DIR"

# 上传必需文件
echo "上传 docker-compose.prod.yml..."
scp docker-compose.prod.yml $SERVER:$REMOTE_DIR/

echo "上传 .env.production.example..."
scp .env.production.example $SERVER:$REMOTE_DIR/

echo "上传部署脚本..."
scp deploy-remote.sh $SERVER:$REMOTE_DIR/

echo "上传文档..."
scp docs/LOCAL_DEPLOYMENT.md $SERVER:$REMOTE_DIR/

echo ""
echo "========================================="
echo "上传完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. SSH 连接到服务器: ssh $SERVER"
echo "2. 创建 .env 文件: cp .env.production.example .env"
echo "3. 编辑 .env 文件: nano .env"
echo "4. 执行部署: ./deploy-remote.sh"
