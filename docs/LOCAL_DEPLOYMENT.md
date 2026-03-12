# 本地手动部署指南

本文档介绍如何在本地环境中手动部署和运行学氧助手，不使用 Docker 容器化部署。

---

## 系统要求

### 后端
- Python 3.9+
- pip 20.0+

### 前端
- Node.js 16+
- npm 7+

---

## 快速开始

### 步骤 1: 克隆项目

```bash
git clone <your-repo-url>
cd xueyang
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑环境变量
nano backend/.env
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

### 步骤 3: 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 4: 启动后端服务

```bash
# 在 backend 目录下
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将运行在 `http://localhost:8000`，API 文档可访问 `http://localhost:8000/docs`。

### 步骤 5: 安装前端依赖

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖
npm install
```

### 步骤 6: 配置前端环境变量

```bash
# 创建 .env 文件
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
```

### 步骤 7: 启动前端服务

```bash
# 开发模式运行
npm run dev
```

前端服务默认运行在 `http://localhost:5173`。

---

## 访问应用

- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:8000/api
- **API 文档**: http://localhost:8000/docs

---

## 功能访问

### 统计信息页面
- 路径: `/stats`
- 功能: 展示聊天统计数据和图表

### 详情查看页面
- 路径: `/details`
- 功能: 管理和查看聊天会话详情

### 大模型聊天页面
- 路径: `/chat`
- 功能: 与大模型进行智能对话

---

## 常用命令

### 后端服务管理

```bash
# 启动后端（开发模式，支持热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动后端（生产模式）
uvicorn main:app --host 0.0.0.0 --port 8000

# 启动后端（多进程）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 查看已安装的依赖
pip list
```

### 前端服务管理

```bash
# 开发模式运行
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 查看已安装的依赖
npm list
```

---

## 注意事项

### 1. 环境配置

- **Python版本**: 确保使用 Python 3.9 或更高版本
- **Node.js版本**: 确保使用 Node.js 16 或更高版本
- **虚拟环境**: 推荐使用 Python 虚拟环境隔离依赖

### 2. API 密钥配置

- **必需配置**: 必须在 `.env` 文件中配置有效的 API 密钥
- **密钥安全**: 不要将 API 密钥提交到版本控制系统
- **API 访问**: 确保网络环境可以访问大模型 API 服务

### 3. 端口配置

- **后端端口**: 默认使用 8000 端口，如被占用可修改启动命令
- **前端端口**: 默认使用 5173 端口，可在启动时指定其他端口

### 4. 数据库

- **SQLite**: 使用 SQLite 数据库，无需额外配置
- **数据库文件**: 自动创建在 `backend/data/langgraph_data.db`

---

## 依赖安装问题

### Python 依赖问题

- **代理设置**: 如果网络受限，可配置 pip 代理
  ```bash
  pip install -r requirements.txt --proxy=http://your-proxy:port
  ```

- **依赖冲突**: 如遇到依赖冲突，建议使用虚拟环境
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Node.js 依赖问题

- **npm 缓存**: 如遇到 npm 安装问题，可清理缓存
  ```bash
  npm cache clean --force
  npm install
  ```

- **依赖版本**: 如遇到版本冲突，可使用 `npm ci` 安装
  ```bash
  npm ci
  ```

---

## 故障排查

### 1. 后端服务启动失败

- **端口占用**: 检查 8000 端口是否被占用
  ```bash
  # Windows
  netstat -ano | findstr :8000
  # Linux/Mac
  lsof -i :8000
  ```

- **依赖缺失**: 确保所有依赖已正确安装
  ```bash
  pip list | grep -E "fastapi|langchain|openai"
  ```

- **API 密钥错误**: 检查 `.env` 文件中的 API 密钥是否正确配置

### 2. 前端服务启动失败

- **端口占用**: 检查 5173 端口是否被占用
- **依赖问题**: 确保 Node.js 依赖已正确安装
- **API 基础 URL**: 确保 `.env` 文件中的 `VITE_API_BASE_URL` 配置正确

### 3. 聊天功能异常

- **网络连接**: 确保网络可以访问大模型 API
- **API 密钥权限**: 确保 API 密钥具有相应的权限
- **上下文长度**: 如遇到上下文长度错误，系统会自动压缩上下文

---

## 性能优化

### 1. 后端优化

- **禁用调试模式**: 生产环境中移除 `--reload` 参数
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000
  ```

- **使用多进程**: 生产环境中可使用多进程运行
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
  ```

### 2. 前端优化

- **生产构建**: 部署时使用生产构建
  ```bash
  npm run build
  ```

- **静态资源压缩**: 构建过程会自动压缩静态资源

---

## 数据备份

### 备份数据库

```bash
# 备份 SQLite 数据库
cp backend/data/langgraph_data.db backend/data/langgraph_data_backup_$(date +%Y%m%d).db
```

### 恢复数据库

```bash
# 恢复 SQLite 数据库
cp backend/data/langgraph_data_backup_20250312.db backend/data/langgraph_data.db
```

---

## 常见问题

### Q: 为什么 API 调用失败？
A: 检查 API 密钥是否正确，网络是否可以访问 API 服务，以及 API 配额是否充足。

### Q: 为什么聊天响应很慢？
A: 大模型响应速度取决于模型性能、网络延迟和请求复杂度。可尝试简化问题或使用更快速的模型。

### Q: 如何查看 API 调用日志？
A: 后端服务启动时会输出详细日志，可查看控制台输出。

### Q: 如何备份聊天数据？
A: 聊天数据存储在 `backend/data/langgraph_data.db` 文件中，可定期备份此文件。

---

## 自动化部署

如需使用 Gitee CI/CD 自动部署，请参考项目中的 CI/CD 配置文件（位于 `.workflow/` 目录）。

**注意**: 本文档仅用于本地手动部署，如需远程服务器部署或 CI/CD 自动部署，请参考其他相关文档。

---

**文档版本**: 2.0.0
**更新日期**: 2026-03-12