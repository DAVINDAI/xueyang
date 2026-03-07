# 基础镜像 - 使用 1Panel 镜像（与本地 Python 3.11.14 保持一致）
# 感谢hub.1panel.dev这个镜像，它提供了与本地 Python 3.11.14 版本一致的环境，下载速度快。网上通过docker镜像关键字导流的公司了，好烦躁。
# 我要做一个能帮助别人的，而不是总想着赚钱的人，一个人能花多少钱呢
FROM hub.1panel.dev/library/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/results

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
