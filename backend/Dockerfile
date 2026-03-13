# 阶段 1: 构建基础
FROM hub.1panel.dev/library/python:3.11-slim AS builder

WORKDIR /app

# 安装最小化构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装轻量级依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com \
    && pip install --user --no-cache-dir \
    langchain \
    langchain-openai \
    langchain-community \
    openai \
    tiktoken \
    python-dotenv \
    requests \
    PyJWT \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic \
    pydantic-settings \
    PyPDF2 \
    langgraph \
    tavily-python

# 阶段 2: 运行时
FROM hub.1panel.dev/library/python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制轻量级依赖
COPY --from=builder /root/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/results

# 暴露端口
EXPOSE 8000

# 启动命令（运行时安装大体积依赖）
CMD ["bash", "-c", "pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && pip config set global.trusted-host mirrors.aliyun.com && pip install --no-cache-dir torch modelscope playwright llama-index llama-index-embeddings-openai llama-index-embeddings-langchain llama-index-vector-stores-chroma chromadb && uvicorn main:app --host 0.0.0.0 --port 8000"]
