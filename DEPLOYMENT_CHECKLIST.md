# 生产环境部署清单

## 部署前检查

- [ ] 服务器已安装 Docker 和 Docker Compose
- [ ] 服务器已登录阿里云镜像仓库
- [ ] 已复制 `.env.production.example` 为 `.env`
- [ ] 已修改 `.env` 中的所有 API 密钥
- [ ] 已生成安全的 `SECRET_KEY`
- [ ] 已配置防火墙开放 80 和 443 端口

## 部署步骤

### 1. 上传项目文件

```bash
# 方式 1: 使用 rsync（推荐）
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/work/ai_project/xueyang/ user@server-ip:/opt/xueyang/

# 方式 2: 使用 scp
scp -r /Users/work/ai_project/xueyang user@server-ip:/opt/
```

### 2. 配置环境变量

```bash
cd /opt/xueyang
cp .env.production.example .env
nano .env

# 生成安全的 SECRET_KEY
openssl rand -hex 32
```

### 3. 登录镜像仓库

```bash
docker login --username=your-username \
  crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com
```

### 4. 执行部署

```bash
chmod +x deploy.sh stop.sh logs.sh
./deploy.sh
```

### 5. 验证部署

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
./logs.sh

# 测试访问
curl http://localhost
curl http://localhost:8000/docs
```

## 部署后检查

- [ ] 后端服务正常运行
- [ ] 前端服务正常运行
- [ ] API 文档可以访问
- [ ] 日志无错误信息
- [ ] 数据目录权限正确

## 常用命令

```bash
# 查看日志
./logs.sh

# 停止服务
./stop.sh

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 更新镜像
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 故障排查

### 查看详细日志

```bash
# 后端日志
docker compose -f docker-compose.prod.yml logs backend

# 前端日志
docker compose -f docker-compose.prod.yml logs frontend
```

### 检查容器状态

```bash
docker compose -f docker-compose.prod.yml ps
docker inspect xueyang-backend-1
```

### 进入容器调试

```bash
# 进入后端容器
docker exec -it xueyang-backend-1 bash

# 检查环境变量
docker exec xueyang-backend-1 env | grep API_KEY
```

## 安全检查

- [ ] SECRET_KEY 已修改为随机字符串
- [ ] .env 文件权限为 600
- [ ] 防火墙已配置
- [ ] 不必要的端口已关闭
- [ ] 定期备份已配置

## 性能优化

- [ ] 已配置 Docker 资源限制
- [ ] 已启用 Nginx Gzip 压缩
- [ ] 已配置日志轮转
- [ ] 已配置监控告警
