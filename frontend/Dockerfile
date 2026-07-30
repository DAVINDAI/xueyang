# 直接打包已编译产物，不再在 Docker 内构建
FROM hub.1panel.dev/library/nginx:alpine

# 复制 Vue SPA 构建产物
COPY dist /usr/share/nginx/html

# 复制 VitePress 文档构建产物
COPY docs/.vitepress/dist /usr/share/nginx/docs

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制首页
COPY homepage.html /usr/share/nginx/html/homepage.html

# 复制备案图标
COPY src/assets/备案图标.png /usr/share/nginx/html/备案图标.png

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
