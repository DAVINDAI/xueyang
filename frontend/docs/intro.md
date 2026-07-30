# 介绍

学氧助手是一个 AI 驱动的学习助手平台，旨在帮助用户更高效地学习和工作。

## 核心特性

- **多模型 AI 对话** — 支持 GLM-5、Qwen-Plus、DeepSeek-Chat 等多种大模型，提供流畅的流式对话体验
- **编程练习** — AI 自动生成算法题目，支持在线代码提交与智能评测
- **简历优化** — 上传 PDF 简历，AI 分析行业匹配度并提供面试建议
- **笔记管理** — 轻量级 Markdown 笔记系统
- **法律问答** — 基于中国法律文书的 RAG 检索增强生成
- **数据隔离** — 每位用户独立 SQLite + ChromaDB 存储

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python FastAPI + LangChain/LangGraph |
| 数据库 | SQLite（每用户独立） |
| 向量存储 | ChromaDB |
| 部署 | Docker + Nginx + 阿里云 ECS |
