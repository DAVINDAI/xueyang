# 阶段 1: 基础镜像 - 系统依赖
FROM hub.1panel.dev/library/python:3.11-slim AS base

WORKDIR /app

# 设置清华园apt镜像源（清除所有现有配置）
RUN rm -rf /etc/apt/sources.list.d/* && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ trixie-security main contrib non-free" >> /etc/apt/sources.list

# 安装系统依赖
# - gcc/g++: 用于编译 Python 依赖包中需要编译的部分（如 torch、transformers、modelscope 等深度学习库）
# - make: 用于构建和安装某些依赖包
# - curl: 用于下载资源（如模型文件、依赖包等）
# - 其他依赖: 用于 Playwright 浏览器运行
# 这些依赖是运行时和安装 Python 依赖包所必需的基础工具
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 阶段 2: 核心依赖 - 轻量级包
FROM base AS core-deps

# 复制核心依赖文件
COPY requirements-core.txt .

# 安装核心依赖（轻量级）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com \
    && pip install --no-cache-dir -r requirements-core.txt

# 阶段 3: 大体积依赖 - 重量级包
FROM core-deps AS big-deps

# 复制大体积依赖文件
COPY requirements-big.txt .

# 安装大体积依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com \
    && pip install --no-cache-dir -r requirements-big.txt \
    && playwright install chromium --with-deps

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
