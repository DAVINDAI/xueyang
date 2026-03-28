#!/bin/bash
set -e

echo "开始数据库迁移..."

# 执行数据库迁移
python database/migrate.py

echo "数据库迁移完成！"

# 启动应用
echo "启动应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8000