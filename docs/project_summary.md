# 学氧助手 — 项目总结

## 概况

独立设计开发的全栈 AI 学习助手，Vue 3 + FastAPI + LangChain/LangGraph 技术栈。核心功能包括多模型对话、算法编程练习（LangGraph 多轮调试引擎）、简历智能分析、法律文档 RAG 检索等模块。SQLite 按用户隔离存储，ChromaDB 向量检索，已部署在阿里云 ECS 生产环境。

## 工程亮点

**LangGraph 多轮代码调试引擎**：编程练习模块使用 LangGraph 构建「生成修复 → 本地执行 → 条件循环」的有状态推理链路，自动检测语法错误、性能瓶颈，最多 5 轮迭代修复，并在关键节点支持 Human-in-the-Loop 人工介入。

**访客级数据隔离架构**：自研 SQLite per visitor 方案，通过自定义 auth middleware 在 `request.state` 注入 `visitor_id`，所有 CRUD 自动路由到独立数据库，零外部依赖实现租户隔离。

**多模型统一接入**：通过 LangChain OpenAI 兼容层接入 GLM-5（1M 上下文）、Qwen-Plus、DeepSeek、Doubao 四种国产大模型，配合 80% 阈值上下文压缩策略管理长对话。

**SSE 流式响应**：聊天模块绕过 Axios 拦截器，使用原生 `fetch` + `ReadableStream` 解析 SSE 事件，实现逐字渲染、Markdown 实时转换和代码高亮。

## 核心成果

- 完整的前后端分离应用（16 个 API 模块、13 个前端路由），Docker 多阶段构建 + 阿里云 ACR 镜像仓库 + docker-compose 一键部署
- 线上稳定运行，三个子域名（主站、学习页、VitePress 文档站）共用单 Nginx 容器，2C2G 服务器资源利用率合理
- 自建 VitePress 技术文档站，覆盖项目架构、部署流程、排障复盘等内容
