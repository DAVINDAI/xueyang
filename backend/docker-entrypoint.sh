#!/bin/bash
set -e

echo "开始安装Playwright浏览器..."

# 安装Playwright浏览器
playwright install chromium --with-deps

echo "Playwright浏览器安装完成！"

echo "开始数据库迁移..."

# 执行数据库迁移
python database/migrate.py

echo "数据库迁移完成！"

# 启动应用
echo "启动应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8000