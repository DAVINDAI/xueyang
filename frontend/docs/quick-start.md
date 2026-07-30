# 快速开始

## 本地开发

```bash
# 安装依赖
cd frontend && npm install

# 启动前端 (端口 5173)
npm run dev

# 启动后端 (端口 8000)
cd ../backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

或使用一键脚本：

```bash
bash scripts/start.sh
```

## Docker 部署

```bash
bash docker-deploy-local.sh
```

## 环境变量

后端需要以下环境变量：

| 变量 | 说明 |
|------|------|
| `SECRET_KEY` | JWT 签名密钥 |
| `GLM_API_KEY` | 智谱 GLM API Key |
| `QWEN_API_KEY` | 通义千问 API Key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `DASHSCOPE_API_KEY` | DashScope API Key |
| `TAVILY_API_KEY` | Tavily 搜索 API Key |
| `LANGSMITH_API_KEY` | LangSmith 追踪（可选） |
