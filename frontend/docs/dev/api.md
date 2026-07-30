# API 文档

在线 Swagger 文档：访问 [learn.xueyang.me/docs](https://learn.xueyang.me/docs)

## 认证方式

所有 API 支持两种认证：

1. **JWT Bearer Token** — 登录后获取
2. **X-Visitor-ID** — 匿名访客标识，自动生成 UUID

## 通用约定

- 请求/响应 JSON 使用 camelCase（前端自动转换 snake_case）
- 分页参数：`page`、`page_size`
- 错误响应：`{ "code": 400, "message": "...", "detail": "..." }`
