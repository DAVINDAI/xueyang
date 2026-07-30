# 架构设计

## 整体架构

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│   Nginx     │────▶│  FastAPI     │────▶│  SQLite   │
│  (80/443)   │     │  (uvicorn)   │     │ (每用户)   │
└─────────────┘     │  :8000       │     └───────────┘
                    │              │     ┌───────────┐
                    │  LangChain   │────▶│ ChromaDB  │
                    │  LangGraph   │     │ (每用户)   │
                    └──────────────┘     └───────────┘
```

## 数据隔离模型

每位用户拥有独立的：
- SQLite 数据库（对话记录、笔记等）
- ChromaDB 向量存储（语义搜索索引）
- 数据目录：`backend/data/{visitor_id}/`

## API 层

14 个 API Router：
- `chat.py` — 对话和会话管理
- `search.py` — 三路并行搜索
- `coding_playground.py` — 编程练习
- `resume.py` — 简历分析
- `notes.py` — 笔记 CRUD
- `law.py` — 法律 RAG 问答
- 其他：`assistant.py`、`communication.py`、`scheduler.py`、`prompts.py`、`parse.py` 等
