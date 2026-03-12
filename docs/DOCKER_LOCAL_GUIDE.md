# 本地 Docker 运行指南

本文档介绍如何在本地使用 Docker 运行学氧助手，适合需要快速搭建完整环境或测试生产环境配置的用户。

---

## 目录

1. [环境要求](#环境要求)
2. [快速开始](#快速开始)
3. [详细步骤](#详细步骤)
4. [常用操作](#常用操作)
5. [数据持久化](#数据持久化)
6. [故障排查](#故障排查)

---

## 环境要求

### 必需软件

- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 系统要求

- CPU: 2核或以上
- 内存: 4GB 或以上
- 磁盘: 10GB 可用空间

---

## 快速开始

```bash
# 1. 进入项目目录
cd xueyang

# 2. 配置环境变量
cp .env.production.example .env
# 编辑 .env 文件，填入 API 密钥

# 3. 登录镜像仓库
docker login --username=davindai@hotmail.com crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com

# 4. 一键部署
./docker-deploy-local.sh
```

---

## 详细步骤

### 步骤 1: 安装 Docker

#### Windows

1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 安装并启动 Docker Desktop
3. 验证安装：
```bash
docker --version
docker compose version
```

#### macOS

```bash
# 使用 Homebrew 安装
brew install --cask docker

# 启动 Docker
open /Applications/Docker.app

# 验证安装
docker --version
```

#### Linux (Ubuntu/Debian)

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.production.example .env

# 编辑环境变量
# Windows: 使用记事本或 VS Code
notepad .env

# macOS/Linux: 使用 nano 或 vim
nano .env
```

**必须修改的配置项：**

```bash
# API 密钥 - 填入真实的密钥
GLM_API_KEY=your_real_glm_api_key
QWEN_API_KEY=your_real_qwen_api_key
DEEPSEEK_API_KEY=your_real_deepseek_api_key
TAVILY_API_KEY=your_real_tavily_api_key
LANGSMITH_API_KEY=your_real_langsmith_api_key

# 安全密钥 - 建议修改为随机字符串
SECRET_KEY=$(openssl rand -hex 32)
```

### 步骤 3: 登录阿里云镜像仓库

```bash
docker login --username=davindai@hotmail.com crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
```

输入密码后，会显示 `Login Succeeded`。

### 步骤 4: 部署服务

```bash
# 给脚本添加执行权限（Linux/macOS）
chmod +x docker-deploy-local.sh

# 执行部署
./docker-deploy-local.sh
```

部署脚本会自动：
- ✓ 检查 Docker 环境
- ✓ 验证 .env 文件
- ✓ 拉取最新镜像
- ✓ 备份数据（如果有）
- ✓ 启动服务
- ✓ 检查服务健康状态

### 步骤 5: 验证部署

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
./scripts/docker-logs.sh

# 测试后端 API
curl http://localhost:8000/docs

# 测试前端（浏览器访问）
http://localhost
```

---

## 常用操作

### 启动服务

```bash
./docker-deploy-local.sh
```

### 停止服务

```bash
# 方式 1: 使用脚本
./scripts/stop.sh

# 方式 2: 直接使用 docker compose
docker compose -f docker-compose.prod.yml down
```

### 重启服务

```bash
# 方式 1: 停止后重新启动
./scripts/stop.sh
./docker-deploy-local.sh

# 方式 2: 直接重启容器
docker compose -f docker-compose.prod.yml restart
```

### 查看日志

```bash
# 使用脚本（实时跟踪最新 100 行）
./scripts/docker-logs.sh

# 查看所有日志
docker compose -f docker-compose.prod.yml logs

# 查看后端日志
docker compose -f docker-compose.prod.yml logs backend

# 查看前端日志
docker compose -f docker-compose.prod.yml logs frontend

# 实时跟踪日志
docker compose -f docker-compose.prod.yml logs -f
```

### 更新服务

```bash
# 1. 拉取最新镜像
docker compose -f docker-compose.prod.yml pull

# 2. 重新部署
docker compose -f docker-compose.prod.yml up -d

# 3. 查看日志
./scripts/docker-logs.sh
```

### 进入容器

```bash
# 进入后端容器
docker exec -it xueyang-backend-1 bash

# 进入前端容器
docker exec -it xueyang-frontend-1 sh
```

---

## 数据持久化

### 数据存储位置

Docker 容器中的数据通过卷（Volume）持久化到本地：

| 数据类型 | 容器路径 | 本地路径 |
|---------|---------|---------|
| 数据库 | `/app/data` | `./data` |
| 上传文件 | `/app/results` | `./results` |

### 备份数据

```bash
# 创建备份目录
mkdir -p backups

# 备份数据
tar -czf backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ results/
```

### 恢复数据

```bash
# 停止服务
docker compose -f docker-compose.prod.yml down

# 恢复数据
tar -xzf backups/backup_20240101_120000.tar.gz

# 重新启动服务
./docker-deploy-local.sh
```

---

## 故障排查

### 问题 1: 端口被占用

**现象**：服务启动失败，提示端口已被占用

**解决**：
```bash
# 查看端口占用（Windows）
netstat -ano | findstr :80
netstat -ano | findstr :8000

# 查看端口占用（macOS/Linux）
lsof -i :80
lsof -i :8000

# 停止占用端口的服务，或修改 docker-compose.prod.yml 中的端口映射
```

### 问题 2: 无法拉取镜像

**现象**：提示 `unauthorized` 或 `pull access denied`

**解决**：
```bash
# 重新登录镜像仓库
docker logout crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
docker login --username=davindai@hotmail.com crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com

# 手动拉取镜像测试
docker pull crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend:latest
```

### 问题 3: 容器启动后立即退出

**现象**：`docker ps` 看不到运行中的容器

**解决**：
```bash
# 查看容器日志
docker compose -f docker-compose.prod.yml logs backend

# 检查环境变量
cat .env

# 确保 .env 文件格式正确（无 BOM，UTF-8 编码）
```

### 问题 4: API 调用失败

**现象**：前端页面打开，但无法与后端通信

**解决**：
```bash
# 检查后端服务状态
curl http://localhost:8000/docs

# 检查容器网络
docker network ls
docker network inspect xueyang_default

# 查看后端日志
docker compose -f docker-compose.prod.yml logs backend
```

### 问题 5: 磁盘空间不足

**现象**：镜像拉取失败或容器无法启动

**解决**：
```bash
# 查看磁盘使用
df -h

# 清理 Docker 缓存
docker system prune -a

# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune
```

### 问题 6: Windows 下脚本无法运行

**现象**：提示 `bash: ./docker-deploy-local.sh: /bin/bash^M: bad interpreter`

**解决**：
```bash
# 转换换行符
dos2unix docker-deploy-local.sh

# 或使用 Git Bash
# 在 Git Bash 中运行脚本
```

---

## 与本地直接运行的区别

| 特性 | Docker 方式 | 本地直接运行 |
|-----|------------|-------------|
| 环境隔离 | ✅ 完全隔离 | ❌ 依赖本机环境 |
| 启动速度 | 较慢（需拉取镜像） | 较快 |
| 资源占用 | 较高 | 较低 |
| 热重载 | ❌ 需重启容器 | ✅ 支持 |
| 调试方便性 | 一般 | 好 |
| 生产环境一致性 | ✅ 完全一致 | 可能有差异 |

### 选择建议

- **开发调试**：使用本地直接运行（`./scripts/start.sh`）
- **测试生产环境**：使用 Docker 方式
- **正式部署**：使用 Docker 方式

---

## 相关文档

- `docs/LOCAL_RUN_GUIDE.md` - 本地直接运行指南
- `docs/LOCAL_DEPLOYMENT.md` - 本地手动部署指南
- `docs/CI_CD_GUIDE.md` - CI/CD 部署说明

---

**文档版本**: 1.0.0  
**更新日期**: 2026-03-12
