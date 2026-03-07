# 阶段 1: 基础镜像 - 系统依赖
FROM hub.1panel.dev/library/python:3.11-slim AS base

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 阶段 2: 依赖镜像 - Python 依赖
FROM base AS deps

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

# 阶段 3: 应用镜像 - 运行时
FROM deps

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/results

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
