# 远程服务器部署指南

**服务器信息**
- IP: 47.110.67.241
- 用户: root
- 项目目录: /opt/xueyang

---

## 🚀 快速部署步骤

### 步骤 1: SSH 连接到服务器

```bash
ssh root@47.110.67.241
# 输入密码: Pp710027784
```

### 步骤 2: 安装 Docker（如果未安装）

```bash
# 检查 Docker 是否已安装
docker --version

# 如果未安装，执行以下命令
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker
```

### 步骤 3: 创建项目目录

```bash
mkdir -p /opt/xueyang
cd /opt/xueyang
```

### 步骤 4: 上传项目文件

**在本地机器上执行**（不是在服务器上）：

```bash
# 方式 1: 使用 rsync（推荐）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/work/ai_project/xueyang/ root@47.110.67.241:/opt/xueyang/

# 方式 2: 使用 scp
scp -r /Users/work/ai_project/xueyang root@47.110.67.241:/opt/
```

### 步骤 5: 配置环境变量

```bash
# 回到服务器
cd /opt/xueyang

# 复制环境变量模板
cp .env.production.example .env

# 编辑环境变量
nano .env
```

**必须修改的配置**：

```bash
# 填入真实的 API 密钥
GLM_API_KEY=your_real_glm_api_key
QWEN_API_KEY=your_real_qwen_api_key
DEEPSEEK_API_KEY=your_real_deepseek_api_key
TAVILY_API_KEY=your_real_tavily_api_key
LANGSMITH_API_KEY=your_real_langsmith_api_key

# 生成安全的 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
```

### 步骤 6: 登录阿里云镜像仓库

```bash
docker login --username=your-username \
  crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
# 输入密码
```

### 步骤 7: 执行部署

```bash
# 给脚本添加执行权限
chmod +x deploy-remote.sh

# 执行部署
./deploy-remote.sh
```

### 步骤 8: 验证部署

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 测试访问
curl http://localhost
curl http://localhost:8000/docs
```

---

## 📋 详细部署步骤

### 1. 检查服务器环境

```bash
# 检查 Docker
docker --version
docker compose version

# 检查系统资源
free -h
df -h

# 检查端口占用
netstat -tuln | grep -E ':80|:8000'
```

### 2. 上传项目文件

**在本地机器上执行**：

```bash
# 使用 rsync 上传（推荐）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/work/ai_project/xueyang/ root@47.110.67.241:/opt/xueyang/

# 或使用 scp
scp -r /Users/work/ai_project/xueyang root@47.110.67.241:/opt/
```

### 3. 配置环境变量

```bash
# 在服务器上执行
cd /opt/xueyang

# 复制模板
cp .env.production.example .env

# 编辑配置
nano .env

# 生成安全的 SECRET_KEY
openssl rand -hex 32
```

### 4. 登录镜像仓库

```bash
docker login --username=your-username \
  crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
```

### 5. 执行部署

```bash
# 方式 1: 使用部署脚本
chmod +x deploy-remote.sh
./deploy-remote.sh

# 方式 2: 手动部署
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 6. 配置防火墙

```bash
# Ubuntu/Debian
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

### 7. 验证部署

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 测试后端
curl http://localhost:8000/docs

# 测试前端
curl http://localhost:80
```

---

## 🌐 访问应用

部署完成后，您可以通过以下地址访问：

- **前端应用**: http://47.110.67.241
- **后端 API**: http://47.110.67.241:8000
- **API 文档**: http://47.110.67.241:8000/docs

---

## 🔧 常用命令

### 服务管理

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 停止服务
docker compose -f docker-compose.prod.yml down

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 更新服务
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 故障排查

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend

# 进入容器调试
docker exec -it xueyang-backend-1 bash

# 检查环境变量
docker exec xueyang-backend-1 env | grep API_KEY

# 检查容器状态
docker inspect xueyang-backend-1
```

---

## 🔒 安全建议

### 1. 修改服务器密码

```bash
# 修改 root 密码
passwd root

# 或创建新用户
adduser deploy
usermod -aG sudo deploy
```

### 2. 配置 SSH 密钥登录

```bash
# 在本地机器上生成 SSH 密钥
ssh-keygen -t rsa -b 4096

# 复制公钥到服务器
ssh-copy-id root@47.110.67.241

# 禁用密码登录（可选）
nano /etc/ssh/sshd_config
# 设置: PasswordAuthentication no
systemctl reload sshd
```

### 3. 配置防火墙

```bash
# Ubuntu/Debian
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

### 4. 定期备份数据

```bash
# 创建备份目录
mkdir -p /opt/backups

# 手动备份
tar -czf /opt/backups/backup_$(date +%Y%m%d).tar.gz \
  -C /opt/xueyang data results

# 配置自动备份（crontab）
crontab -e
# 添加: 0 2 * * * tar -czf /opt/backups/backup_$(date +\%Y\%m\%d).tar.gz -C /opt/xueyang data results
```

---

## 📊 监控和日志

### 查看实时日志

```bash
# 所有服务日志
docker compose -f docker-compose.prod.yml logs -f

# 特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# 查看最近 100 行日志
docker compose -f docker-compose.prod.yml logs --tail=100
```

### 监控资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

---

## 🔄 更新部署

### 更新镜像

```bash
# 拉取最新镜像
docker compose -f docker-compose.prod.yml pull

# 重新部署
docker compose -f docker-compose.prod.yml up -d

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 更新代码

```bash
# 停止服务
docker compose -f docker-compose.prod.yml down

# 上传新代码（在本地执行）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/work/ai_project/xueyang/ root@47.110.67.241:/opt/xueyang/

# 重新部署
docker compose -f docker-compose.prod.yml up -d
```

---

## 🆘 故障排查

### 问题 1: 服务无法启动

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs

# 检查环境变量
cat .env

# 检查端口占用
netstat -tuln | grep -E ':80|:8000'
```

### 问题 2: 无法拉取镜像

```bash
# 检查登录状态
docker logout
docker login --username=your-username \
  crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com

# 手动拉取
docker pull crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend:latest
```

### 问题 3: 无法访问服务

```bash
# 检查防火墙
ufw status

# 检查服务状态
docker compose -f docker-compose.prod.yml ps

# 检查端口
netstat -tuln | grep -E ':80|:8000'
```

---

## 📞 获取帮助

如果遇到问题，请：

1. 查看日志: `docker compose -f docker-compose.prod.yml logs -f`
2. 检查服务状态: `docker compose -f docker-compose.prod.yml ps`
3. 检查环境变量: `cat .env`
4. 参考 [DEPLOYMENT.md](file:///Users/work/ai_project/xueyang/DEPLOYMENT.md) 文档
