# Docker部署数据库迁移指南

## 方案概述

在Docker部署环境下，数据库迁移脚本 `database/migrate.py` 会在容器启动时自动执行。

## 实现方式

### 1. 自动执行（推荐）

我们创建了一个 `docker-entrypoint.sh` 脚本，在容器启动时自动执行数据库迁移：

```bash
#!/bin/bash
set -e

echo "开始数据库迁移..."

# 执行数据库迁移
python database/migrate.py

echo "数据库迁移完成！"

# 启动应用
echo "启动应用..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Dockerfile配置

修改了Dockerfile，使用entrypoint脚本：

```dockerfile
# 复制数据库迁移脚本
COPY docker-entrypoint.sh /app/

# 给entrypoint脚本添加执行权限
RUN chmod +x /app/docker-entrypoint.sh

# 启动命令（使用entrypoint脚本）
CMD ["/app/docker-entrypoint.sh"]
```

## 使用方法

### 构建Docker镜像

```bash
cd backend
docker build -t xueyang-backend .
```

### 运行Docker容器

```bash
docker run -d \
  --name xueyang-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  xueyang-backend
```

### 查看日志

```bash
docker logs xueyang-backend
```

## 执行流程

1. **容器启动**：Docker容器启动时执行 `docker-entrypoint.sh`
2. **数据库迁移**：脚本自动执行 `python database/migrate.py`
3. **表创建**：在 `/app/data/xueyang.db` 中创建 `goals` 和 `tasks` 表
4. **应用启动**：迁移完成后启动FastAPI应用
5. **服务就绪**：应用监听在 `0.0.0.0:8000`

## 手动执行（可选）

如果需要在运行中的容器中手动执行数据库迁移：

```bash
# 进入容器
docker exec -it xueyang-backend bash

# 手动执行迁移
python database/migrate.py

# 退出容器
exit
```

## 数据持久化

使用Docker卷来持久化数据库：

```bash
docker run -d \
  --name xueyang-backend \
  -p 8000:8000 \
  -v xueyang-data:/app/data \
  xueyang-backend
```

这样即使容器重启，数据库数据也会保留。

## 故障排除

### 查看迁移日志

```bash
docker logs xueyang-backend | grep "数据库迁移"
```

### 检查数据库文件

```bash
docker exec xueyang-backend ls -la /app/data/
```

### 进入容器检查

```bash
docker exec -it xueyang-backend bash
python -c "import sqlite3; conn = sqlite3.connect('data/xueyang.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([row[0] for row in cursor.fetchall()])"
```

## 注意事项

1. **权限问题**：确保Docker容器有权限写入 `/app/data` 目录
2. **数据库路径**：在容器中数据库路径为 `/app/data/xueyang.db`
3. **自动执行**：每次容器重启都会执行迁移脚本，但脚本会检查表是否已存在
4. **幂等性**：迁移脚本使用 `CREATE TABLE IF NOT EXISTS`，可以安全重复执行

## 生产环境建议

在生产环境中，建议：

1. 使用环境变量控制是否执行迁移
2. 添加迁移版本控制
3. 记录迁移日志
4. 备份现有数据库

示例：

```bash
docker run -d \
  --name xueyang-backend \
  -p 8000:8000 \
  -v xueyang-data:/app/data \
  -e RUN_MIGRATION=true \
  xueyang-backend
```