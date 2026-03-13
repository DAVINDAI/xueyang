# 阶段 1: 构建依赖
FROM hub.1panel.dev/library/python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖到用户目录
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --user --no-cache-dir -r requirements.txt

# 阶段 2: 运行时
FROM hub.1panel.dev/library/python:3.11-slim

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /root/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/results

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
