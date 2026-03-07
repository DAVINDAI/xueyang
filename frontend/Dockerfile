# 构建阶段 - 使用 1Panel 镜像
FROM hub.1panel.dev/library/node:22-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package*.json .

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 构建应用
RUN npm run build

# 运行阶段 - 使用 1Panel 镜像
FROM hub.1panel.dev/library/nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["nginx", "-g", "daemon off;"]
