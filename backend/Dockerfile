# 阶段 1: 基础镜像 - 系统依赖
FROM hub.1panel.dev/library/python:3.11-slim AS base

WORKDIR /app

# 设置清华园apt镜像源
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bullseye-security main contrib non-free" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 阶段 2: 核心依赖 - 轻量级包
FROM base AS core-deps

# 复制核心依赖文件
COPY requirements-core.txt .

# 安装核心依赖（轻量级）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn \
    && pip install --no-cache-dir -r requirements-core.txt

# 阶段 3: 大体积依赖 - 重量级包
FROM core-deps AS big-deps

# 复制大体积依赖文件
COPY requirements-big.txt .

# 安装大体积依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn \
    && pip install --no-cache-dir -r requirements-big.txt

# 阶段 4: 应用镜像 - 运行时
FROM big-deps

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/results

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
