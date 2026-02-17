# LangGraph Chat 本地运行指南

本文档介绍如何在本地环境中运行LangGraph Chat应用，无需使用Docker容器化部署。

## 系统要求

### 后端
- Python 3.9+
- pip 20.0+

### 前端
- Node.js 16+
- npm 7+

## 后端服务运行

### 步骤1: 安装Python依赖

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt
```

### 步骤2: 配置环境变量

复制`.env.example`文件为`.env`，并填写API密钥：

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，填写API密钥
# GLM_API_KEY=your_glm_api_key
# QWEN_API_KEY=your_qwen_api_key
# GLM_API_BASE=https://api.example.com/glm5
# QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 步骤3: 启动后端服务

```bash
# 启动FastAPI服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将运行在 `http://localhost:8000`，API文档可访问 `http://localhost:8000/docs`。

## 前端服务运行

### 步骤1: 安装Node.js依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 步骤2: 配置环境变量

在前端根目录创建`.env`文件，配置API基础URL：

```bash
# 创建.env文件
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
```

### 步骤3: 运行前端服务

#### 开发模式运行

```bash
# 开发模式运行
npm run dev
```

前端服务默认运行在 `http://localhost:5173`。

#### 构建后运行

```bash
# 构建前端
npm run build

# 使用本地服务器运行构建结果
npm run preview
```

## 访问应用

1. **前端应用**: `http://localhost:5173`
2. **后端API**: `http://localhost:8000/api`
3. **API文档**: `http://localhost:8000/docs`

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

## 注意事项

### 1. 环境配置

- **Python版本**: 确保使用Python 3.9或更高版本
- **Node.js版本**: 确保使用Node.js 16或更高版本
- **虚拟环境**: 推荐使用Python虚拟环境隔离依赖

### 2. API密钥配置

- **必需配置**: 必须在`.env`文件中配置有效的API密钥
- **密钥安全**: 不要将API密钥提交到版本控制系统
- **API访问**: 确保网络环境可以访问大模型API服务

### 3. 端口配置

- **后端端口**: 默认使用8000端口，如被占用可修改启动命令
- **前端端口**: 默认使用5173端口，可在启动时指定其他端口

### 4. 数据库

- **SQLite**: 使用SQLite数据库，无需额外配置
- **数据库文件**: 自动创建在`data/langgraph_data.db`

### 5. 依赖安装问题

#### Python依赖问题

- **代理设置**: 如果网络受限，可配置pip代理
  ```bash
  pip install -r requirements.txt --proxy=http://your-proxy:port
  ```

- **依赖冲突**: 如遇到依赖冲突，建议使用虚拟环境
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

#### Node.js依赖问题

- **npm缓存**: 如遇到npm安装问题，可清理缓存
  ```bash
  npm cache clean --force
  npm install
  ```

- **依赖版本**: 如遇到版本冲突，可使用`npm ci`安装
  ```bash
  npm ci
  ```

## 故障排除

### 1. 后端服务启动失败

- **端口占用**: 检查8000端口是否被占用
  ```bash
  lsof -i :8000  # macOS/Linux
  netstat -ano | findstr :8000  # Windows
  ```

- **依赖缺失**: 确保所有依赖已正确安装
  ```bash
  pip list | grep -E "fastapi|langchain|openai"
  ```

- **API密钥错误**: 检查.env文件中的API密钥是否正确配置

### 2. 前端服务启动失败

- **端口占用**: 检查5173端口是否被占用
- **依赖问题**: 确保Node.js依赖已正确安装
- **API基础URL**: 确保.env文件中的VITE_API_BASE_URL配置正确

### 3. 聊天功能异常

- **网络连接**: 确保网络可以访问大模型API
- **API密钥权限**: 确保API密钥具有相应的权限
- **上下文长度**: 如遇到上下文长度错误，系统会自动压缩上下文

## 性能优化

### 1. 后端优化

- **禁用调试模式**: 生产环境中移除`--reload`参数
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

## 常见问题

### Q: 为什么API调用失败？
A: 检查API密钥是否正确，网络是否可以访问API服务，以及API配额是否充足。

### Q: 为什么聊天响应很慢？
A: 大模型响应速度取决于模型性能、网络延迟和请求复杂度。可尝试简化问题或使用更快速的模型。

### Q: 如何查看API调用日志？
A: 后端服务启动时会输出详细日志，可查看控制台输出。

### Q: 如何备份聊天数据？
A: 聊天数据存储在`data/langgraph_data.db`文件中，可定期备份此文件。

## 联系与支持

如遇到问题，请检查以上故障排除步骤，或参考项目文档获取更多信息。

---

**文档版本**: 1.0.0
**更新日期**: 2026-02-14
