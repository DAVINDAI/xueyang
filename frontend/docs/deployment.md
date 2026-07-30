# 部署指南

## 服务器要求

- 2C2G 最低配置（推荐 4C8G）
- Ubuntu 20.04+ / CentOS 8+
- Docker 20.10+
- Docker Compose v2+

## 生产部署

```bash
# 拉取代码
git clone https://gitee.com/davindai/xueyang.git
cd xueyang

# 配置 SSL 证书
mkdir ssl
# 将证书文件放入 ssl/ 目录：
#   xueyang.me.pem / xueyang.me.key
#   learn.xueyang.me.pem / learn.xueyang.me.key

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys

# 启动
bash docker-deploy-server.sh
```

## 域名配置

| 域名 | 用途 |
|------|------|
| `xueyang.me` | 首页/落地页 |
| `learn.xueyang.me` | 学氧助手 Web 应用 |
| `docs.xueyang.me` | 文档站点 |
| `project.xueyang.me` | 项目展示（代理到其他服务器） |

## 数据备份

用户数据存储在 `./data/` 目录：

```bash
# 定时备份
cp -r data/ data-backup-$(date +%Y%m%d)/
```
