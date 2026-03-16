# CI/CD 打包和部署说明

本文档详细说明 Gitee CI/CD 流水线（pipeline-20260306）的配置逻辑和部署流程。

---

## 概述

本项目使用 Gitee Go CI/CD 实现自动化打包和部署。当代码推送到 `main` 分支时，会自动触发整个流水线。

**流水线名称**: pipeline-20260306  
**触发条件**: 代码推送到 `main` 分支  
**部署目标**: 阿里云 ECS 服务器（47.110.67.241）

---

## 流水线阶段

整个流水线分为 **4 个阶段**，按顺序执行：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Docker构建  │ → │   Python打包  │ → │   发布上传   │ → │   主机部署   │
│  (镜像构建)  │    │  (制品准备)   │    │  (制品上传)  │    │  (服务部署)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 阶段一：Docker 镜像构建

### 目的
构建后端和前端的 Docker 镜像，并推送到阿里云镜像仓库。

### 配置详情

#### 1. 后端镜像构建

```yaml
step: build@docker
name: backend_build_docker
displayName: backend镜像构建
repository: crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me
tag: backend
dockerfile: backend/Dockerfile
context: backend
processorType: amd64
```

**逻辑说明**：
- 使用 `backend/Dockerfile` 构建镜像
- 构建上下文为 `backend/` 目录
- 镜像标签为 `backend`
- 推送到阿里云个人镜像仓库
- 支持 AMD64 架构

#### 2. 前端镜像构建

```yaml
step: build@docker
name: frontend_build_docker
displayName: frontend镜像构建
repository: crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me
tag: frontend
dockerfile: ./frontend/Dockerfile
context: ./frontend
processorType: amd64
```

**逻辑说明**：
- 使用 `frontend/Dockerfile` 构建镜像
- 构建上下文为 `frontend/` 目录
- 镜像标签为 `frontend`
- 与后端镜像推送到同一仓库

### 镜像仓库信息
- **仓库地址**: `crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me`
- **登录用户**: davindai@hotmail.com
- **镜像命名**: 
  - 后端: `xueyang_me:backend`
  - 前端: `xueyang_me:frontend`

---

## 阶段二：Python 构建（制品打包）

### 目的
准备部署所需的配置文件和脚本，打包成制品。

### 配置详情

```yaml
step: build@python
name: build_python
displayName: Python 构建
pythonVersion: '3.11'
commands:
  - pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  - python --version
  - ls -la
  - mkdir output
  - cp server-deploy.sh output/
  - cp docker-compose.prod.yml output/
artifacts:
  - name: BUILD_ARTIFACT
    path:
      - ./output
```

### 逻辑说明

1. **环境配置**
   - 使用 Python 3.11
   - 配置清华 PyPI 镜像源（加速依赖下载）

2. **制品准备**
   - 创建 `output/` 目录
   - 复制部署脚本：`server-deploy.sh`
   - 复制 Docker Compose 配置：`docker-compose.prod.yml`

3. **制品输出**
   - 将 `output/` 目录作为构建制品
   - 制品名称为 `BUILD_ARTIFACT`

### 打包内容

| 文件 | 说明 |
|------|------|
| `server-deploy.sh` | 服务器部署脚本，负责拉取镜像并启动服务 |
| `docker-compose.prod.yml` | 生产环境 Docker Compose 配置 |

---

## 阶段三：发布上传

### 目的
将阶段二打包的制品上传到 Gitee 制品仓库。

### 配置详情

```yaml
step: publish@general_artifacts
name: publish_general_artifacts
displayName: 上传制品
dependArtifact: BUILD_ARTIFACT
artifactName: output
```

### 逻辑说明

- **依赖制品**: 使用阶段二生成的 `BUILD_ARTIFACT`
- **制品名称**: 上传后命名为 `output`
- **存储位置**: Gitee 默认制品仓库

---

## 阶段四：主机部署

### 目的
在目标服务器上执行部署操作，更新服务。

### 配置详情

```yaml
step: deploy@agent
name: deploy_agent
displayName: 主机部署
hostGroupID:
  ID: ecs2c2g
  hostID:
    - 930dbfdf-68f5-4a9e-8901-3299e74b1aa4
deployArtifact:
  - source: artifact
    name: output
    target: ~/gitee_go/deploy
    artifactName: output
    artifactVersion: latest
script:
  - cd /opt/xueyang
  - tar zxvf ~/gitee_go/deploy/output.tar.gz -C /opt/xueyang/
  - mv -f output/* .
  - ls -la /opt/xueyang/
  - ls -la
  - sh server-deploy.sh
```

### 部署脚本逻辑详解

#### 1. 服务器信息
- **主机组**: ecs2c2g
- **主机 ID**: 930dbfdf-68f5-4a9e-8901-3299e74b1aa4
- **部署目录**: `/opt/xueyang`
- **制品临时目录**: `~/gitee_go/deploy`

#### 2. 部署流程

```bash
# 1. 进入项目目录
cd /opt/xueyang

# 2. 解压制品包到项目目录
tar zxvf ~/gitee_go/deploy/output.tar.gz -C /opt/xueyang/

# 3. 移动文件到根目录
mv -f output/* .

# 4. 查看文件列表（调试用）
ls -la /opt/xueyang/
ls -la

# 5. 执行部署脚本
sh server-deploy.sh
```

#### 3. 部署脚本执行流程

`server-deploy.sh` 通常会执行以下操作：

```bash
# 1. 拉取最新镜像
docker pull crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me:backend
docker pull crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me:frontend

# 2. 停止现有服务
docker-compose -f docker-compose.prod.yml down

# 3. 启动新服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 清理旧镜像
docker image prune -f
```

---

## 完整部署流程图

```
代码推送到 main 分支
        │
        ▼
┌─────────────────┐
│  触发 CI/CD 流水线 │
└─────────────────┘
        │
        ▼
┌─────────────────┐     ┌─────────────────┐
│  构建后端 Docker  │     │  构建前端 Docker  │
│     镜像        │     │     镜像        │
└─────────────────┘     └─────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌─────────────────┐
        │  推送镜像到阿里云  │
        │   镜像仓库       │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │  打包部署脚本和   │
        │  Docker Compose  │
        │   配置文件      │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │  上传制品到      │
        │  Gitee 制品仓库  │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │  在服务器上解压   │
        │   制品包        │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │  执行部署脚本    │
        │  拉取镜像并启动  │
        │   服务          │
        └─────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │   部署完成！     │
        └─────────────────┘
```

---

## 关键文件说明

### 1. docker-compose.prod.yml
生产环境的 Docker Compose 配置，定义了：
- 后端服务的容器配置
- 前端服务的容器配置
- 网络设置
- 卷挂载

### 2. server-deploy.sh
服务器部署脚本，负责：
- 登录镜像仓库
- 拉取最新镜像
- 停止旧服务
- 启动新服务
- 清理资源

### 3. Dockerfile（后端/前端）
定义了镜像构建步骤：
- 基础镜像选择
- 依赖安装
- 代码复制
- 启动命令

---

## 注意事项

### 1. 环境变量配置
部署前需要确保服务器上的 `.env` 文件已正确配置：
- API 密钥（GLM、Qwen、DeepSeek 等）
- 数据库配置
- 其他敏感信息

### 2. 镜像仓库权限
确保 CI/CD 有权限推送镜像到阿里云镜像仓库。

### 3. 服务器准备
目标服务器需要：
- 安装 Docker 和 Docker Compose
- 配置正确的 `.env` 文件
- 有权限执行部署脚本

### 4. 部署失败排查
如果部署失败，可以检查：
- Gitee CI/CD 日志
- 服务器上的部署日志
- Docker 容器状态：`docker ps -a`
- 容器日志：`docker logs <container_id>`

---

## 相关文档

- `docs/DEPLOYMENT.md` - 部署指南
- `docs/LOCAL_DEPLOYMENT.md` - 本地部署指南
- `docs/ARCHITECTURE_OPENCLAW.md` - 架构文档

---

**文档版本**: 1.0.0  
**更新日期**: 2026-03-12
