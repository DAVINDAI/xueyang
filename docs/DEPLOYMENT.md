# 生产环境部署指南

## 目录

1. [服务器要求](#服务器要求)
2. [部署前准备](#部署前准备)
3. [快速部署](#快速部署)
4. [详细步骤](#详细步骤)
5. [配置 HTTPS](#配置-https)
6. [常用命令](#常用命令)
7. [故障排查](#故障排查)

---

## 服务器要求

### 硬件要求

- CPU: 2核或以上
- 内存: 4GB 或以上
- 磁盘: 20GB 或以上

### 软件要求

- 操作系统: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- Docker: 20.10+
- Docker Compose: 2.0+

---

## 部署前准备

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 2. 安装 Docker Compose

```bash
# Docker Compose 已包含在 Docker 中，验证安装
docker compose version
```

### 3. 登录阿里云镜像仓库

```bash
docker login --username=your-username crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
```

---

## 快速部署

```bash
# 1. 克隆项目（或上传项目文件）
git clone <your-repo-url>
cd xueyang

# 2. 配置环境变量
cp .env.production.example .env
nano .env  # 编辑并填入真实的 API 密钥

# 3. 给脚本添加执行权限
chmod +x deploy.sh stop.sh logs.sh

# 4. 一键部署
./deploy.sh
```

---

## 详细步骤

### 步骤 1: 上传项目文件

#### 方式 1: 使用 Git

```bash
git clone <your-repo-url>
cd xueyang
```

#### 方式 2: 使用 SCP 上传

```bash
# 在本地机器上执行
scp -r /Users/work/ai_project/xueyang user@server-ip:/opt/
```

#### 方式 3: 使用 rsync 同步

```bash
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/work/ai_project/xueyang/ user@server-ip:/opt/xueyang/
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.production.example .env

# 编辑环境变量
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

# 安全密钥 - 必须修改为随机字符串！
SECRET_KEY=$(openssl rand -hex 32)
```

### 步骤 3: 登录镜像仓库

```bash
docker login --username=your-username crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
```

输入密码后，会显示 `Login Succeeded`。

### 步骤 4: 部署服务

```bash
# 给脚本添加执行权限
chmod +x deploy.sh stop.sh logs.sh

# 执行部署
./deploy.sh
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
./logs.sh

# 测试后端 API
curl http://localhost:8000/docs

# 测试前端
curl http://localhost:80
```

---

## 配置 HTTPS

### 方式 1: 使用 Let's Encrypt（推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 方式 2: 使用自定义证书

1. 准备证书文件：
   - `your-domain.com.crt` - SSL 证书
   - `your-domain.com.key` - 私钥文件

2. 创建证书目录：
```bash
sudo mkdir -p /etc/nginx/ssl
sudo cp your-domain.com.crt /etc/nginx/ssl/
sudo cp your-domain.com.key /etc/nginx/ssl/
```

3. 使用 Nginx 配置：
```bash
# 复制配置文件
sudo cp nginx.conf.example /etc/nginx/sites-available/xueyang

# 修改域名和证书路径
sudo nano /etc/nginx/sites-available/xueyang

# 启用配置
sudo ln -s /etc/nginx/sites-available/xueyang /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 常用命令

### 服务管理

```bash
# 启动服务
./deploy.sh

# 停止服务
./stop.sh

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 查看日志
./logs.sh

# 查看服务状态
docker compose -f docker-compose.prod.yml ps
```

### 更新部署

```bash
# 1. 拉取最新镜像
docker compose -f docker-compose.prod.yml pull

# 2. 重新部署
docker compose -f docker-compose.prod.yml up -d

# 3. 查看日志
./logs.sh
```

### 数据管理

```bash
# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/ results/

# 恢复数据
tar -xzf backup_20240101.tar.gz
```

---

## 故障排查

### 问题 1: 服务无法启动

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend

# 检查容器状态
docker compose -f docker-compose.prod.yml ps

# 检查环境变量
docker exec xueyang-backend-1 env | grep API_KEY
```

### 问题 2: 无法拉取镜像

```bash
# 检查登录状态
docker logout
docker login --username=your-username crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com

# 手动拉取镜像
docker pull crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend:latest
```

### 问题 3: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :80
sudo lsof -i :8000

# 停止占用端口的服务
sudo systemctl stop nginx  # 如果 Nginx 占用了 80 端口
```

### 问题 4: 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 Docker 缓存
docker system prune -a

# 清理未使用的镜像
docker image prune -a
```

### 问题 5: API 密钥无效

```bash
# 检查环境变量是否正确
cat .env

# 重启服务使配置生效
docker compose -f docker-compose.prod.yml restart
```

---

## 安全建议

1. **修改默认密钥**
   - 必须修改 `SECRET_KEY` 为安全的随机字符串
   - 使用 `openssl rand -hex 32` 生成

2. **配置防火墙**
```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

3. **定期备份数据**
```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * cd /opt/xueyang && tar -czf /opt/backups/backup_$(date +\%Y\%m\%d).tar.gz data/ results/
```

4. **监控日志**
```bash
# 实时监控日志
./logs.sh

# 查看错误日志
docker compose -f docker-compose.prod.yml logs | grep -i error
```

---

## 性能优化

1. **调整 Docker 资源限制**

编辑 `docker-compose.prod.yml`：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

2. **启用 Gzip 压缩**

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

---

## 联系支持

如有问题，请查看：
- 项目文档: README.md
- 日志文件: 使用 `./logs.sh` 查看
- Docker 文档: https://docs.docker.com/
