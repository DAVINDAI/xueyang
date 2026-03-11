# 学氧助手 (XueYang) 项目架构说明文档

> 📝 **文档生成**: 由 OpenClaw 自动分析生成  
> 📅 **生成时间**: 2026-03-08  
> 📂 **项目路径**: D:\xueyang

---

## 一、项目概述

### 1.1 项目简介

**学氧助手** 是一个基于 AI 技术的终身学习助手平台，旨在通过人工智能技术为学习者提供个性化、智能化的学习支持。

**核心理念**: 让学习像呼吸一样自然

### 1.2 核心功能模块

| 模块 | 功能描述 |
|------|----------|
| 🤖 AI 对话 | 基于大模型的智能问答系统，支持多模型切换 |
| 📝 备忘录 | 智能笔记管理与知识整理，自动提取对话要点 |
| 📄 笔记管理 | Markdown 编辑器支持的个人笔记管理系统 |
| 📄 简历优化 | AI 辅助简历撰写与优化，提供行业分析和面试准备 |
| 📊 数据分析 | 学习数据可视化与统计 |

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Web 浏览器  │  │   移动端    │  │   API 调用   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Vue 3 + Vite + Element Plus + Vue Router           │   │
│  │  - 组件化开发                                        │   │
│  │  - 路由管理                                          │   │
│  │  - 状态管理                                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端层 (Backend)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python)                                   │   │
│  │  - JWT 身份认证                                      │   │
│  │  - CORS 跨域支持                                     │   │
│  │  - RESTful API 设计                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  业务服务层 (Services)                              │   │
│  │  - LLM 服务 (LangChain + LangGraph)                 │   │
│  │  - 数据库服务 (SQLite)                              │   │
│  │  - 记忆管理服务                                      │   │
│  │  - Token 管理服务                                    │   │
│  │  - PDF 处理服务                                      │   │
│  │  - 网页抓取服务 (Playwright)                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SQLite 数据库                                      │   │
│  │  - chat_session (聊天会话表)                        │   │
│  │  - chat_message (聊天消息表)                        │   │
│  │  - memo_message (备忘录表)                          │   │
│  │  - resume_optimization (简历优化表)                 │   │
│  │  - notes (笔记表)                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  外部 API 服务                                       │   │
│  │  - 智谱 AI (GLM)                                    │   │
│  │  - 通义千问 (Qwen)                                  │   │
│  │  - DeepSeek                                         │   │
│  │  - Tavily 搜索                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈详情

#### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.25 | 核心框架 |
| Vite | 7.3.1 | 构建工具 |
| Element Plus | 2.13.2 | UI 组件库 |
| Vue Router | 4.6.4 | 路由管理 |
| Axios | 1.13.5 | HTTP 客户端 |
| ECharts | 6.0.0 | 数据可视化 |
| Marked | 17.0.2 | Markdown 解析 |
| Mermaid | 11.12.2 | 流程图绘制 |
| Highlight.js | 11.11.1 | 代码高亮 |

#### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | >=0.100.0 | Web 框架 |
| Uvicorn | >=0.23.0 | ASGI 服务器 |
| LangChain | >=0.3.0 | AI 应用框架 |
| LangGraph | >=0.2.0 | 状态管理/工作流 |
| PyJWT | >=2.6.0 | JWT 认证 |
| SQLite | 内置 | 数据库 |
| PyPDF2 | >=3.0.0 | PDF 解析 |
| Playwright | >=1.40.0 | 浏览器自动化 |
| Tiktoken | >=0.5.0 | Token 计算 |

---

## 三、目录结构

```
xueyang/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── api/                     # API 路由层
│   │   │   ├── auth.py             # 认证接口
│   │   │   ├── chat.py             # 聊天接口
│   │   │   ├── details.py          # 详情接口
│   │   │   ├── notes.py            # 笔记接口
│   │   │   ├── resume.py           # 简历接口
│   │   │   ├── search.py           # 搜索接口
│   │   │   └── stats.py            # 统计接口
│   │   ├── config/                  # 配置模块
│   │   │   └── __init__.py         # 模型配置
│   │   ├── models/                  # 数据模型
│   │   │   └── __init__.py
│   │   └── services/                # 业务服务层
│   │       ├── db.py               # 数据库服务
│   │       ├── llm.py              # 大模型服务
│   │       ├── memory.py           # 记忆管理
│   │       ├── tokenizer.py        # Token 管理
│   │       ├── pdf_processor.py    # PDF 处理
│   │       ├── resume_optimizer.py # 简历优化
│   │       └── web_scraper.py      # 网页抓取
│   ├── browser_context/             # 浏览器上下文
│   ├── main.py                      # 应用入口
│   ├── requirements.txt             # Python 依赖
│   └── Dockerfile                   # Docker 配置
│
├── frontend/                         # 前端应用
│   ├── public/                      # 静态资源
│   ├── src/
│   │   ├── api/                     # API 调用封装
│   │   │   ├── authApi.js          # 认证 API
│   │   │   ├── resumeApi.js        # 简历 API
│   │   │   └── index.js            # API 导出
│   │   ├── assets/                  # 资源文件
│   │   ├── components/              # 公共组件
│   │   │   ├── HelloWorld.vue
│   │   │   └── SearchBar.vue
│   │   ├── router/                  # 路由配置
│   │   │   └── index.js
│   │   ├── views/                   # 页面组件
│   │   │   ├── ChatPage.vue        # 聊天页面
│   │   │   ├── DetailsPage.vue     # 详情页面
│   │   │   ├── HomeView.vue        # 首页
│   │   │   ├── LoginPage.vue       # 登录页面
│   │   │   ├── MemoPage.vue        # 备忘录页面
│   │   │   ├── NotesPage.vue       # 笔记页面
│   │   │   ├── ResumeList.vue      # 简历列表
│   │   │   ├── ResumeOptimizer.vue # 简历优化
│   │   │   └── StatsPage.vue       # 统计页面
│   │   ├── App.vue                  # 根组件
│   │   └── main.js                  # 入口文件
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # Node 依赖
│   ├── vite.config.js              # Vite 配置
│   └── Dockerfile                   # Docker 配置
│
├── data/                            # 数据目录 (运行时生成)
│   └── langgraph_data.db           # SQLite 数据库
│
├── .workflow/                       # CI/CD 工作流
│   ├── branch-pipeline.yml
│   ├── master-pipeline.yml
│   └── pr-pipeline.yml
│
├── .gitee/                          # Gitee 配置
│   ├── ISSUE_TEMPLATE.zh-CN.md
│   └── PULL_REQUEST_TEMPLATE.zh-CN.md
│
├── docker-compose.yml               # Docker Compose 配置
├── docker-compose.prod.yml          # 生产环境配置
├── nginx.conf.example               # Nginx 配置示例
├── deploy.sh                        # 部署脚本
├── start.sh                         # 启动脚本
└── stop.sh                          # 停止脚本
```

---

## 四、核心模块详解

### 4.1 认证模块 (Auth)

**功能**: JWT 令牌认证

**流程**:
1. 用户发送手机号获取验证码 (`/api/auth/send-code`)
2. 用户输入验证码登录 (`/api/auth/login`)
3. 后端验证后返回 JWT Token
4. 前端将 Token 存储到 localStorage
5. 后续请求在 Authorization 头中携带 Token

**排除认证的路径**:
- `/api/auth/send-code`
- `/api/auth/login`
- `/`
- `/health`
- `/docs`
- `/openapi.json`
- `/redoc`
- `/api/chat/memos/*`

### 4.2 聊天模块 (Chat)

**核心功能**:
- 创建/管理聊天会话
- 发送消息 (支持流式输出)
- 备忘录功能 (输入"记一下"或"m"自动提取对话要点)
- 上下文压缩 (当 token 数达到阈值时自动压缩历史对话)

**API 端点**:
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chat/sessions` | POST | 创建会话 |
| `/api/chat/sessions` | GET | 获取会话列表 |
| `/api/chat/sessions/{id}` | GET/PUT/DELETE | 会话详情/更新/删除 |
| `/api/chat/messages/{session_id}` | GET | 获取消息列表 |
| `/api/chat/completion` | POST | 聊天 (非流式) |
| `/api/chat/completion/stream` | POST | 聊天 (流式) |
| `/api/chat/memos` | GET | 获取备忘录列表 |
| `/api/chat/memos/{id}` | GET/DELETE | 备忘录详情/删除 |

### 4.3 大模型服务 (LLM Service)

**支持的模型**:
| 模型 | 上下文长度 | API 提供商 |
|------|-----------|-----------|
| glm-5 | 100 万 token | 智谱 AI |
| qwen-plus | 20 万 token | 通义千问 |
| deepseek-chat | 128k token | DeepSeek |

**核心特性**:
- 多模型支持，可动态切换
- 会话记忆管理 (LangChain Memory)
- Token 计数与上下文压缩
- 流式输出支持

### 4.4 数据库设计

**表结构**:

#### chat_session (聊天会话表)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键 |
| session_name | TEXT | 会话名称 |
| model_name | TEXT | 使用的模型 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### chat_message (聊天消息表)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 会话 ID (外键) |
| role | TEXT | 角色 (user/assistant) |
| content | TEXT | 消息内容 |
| created_at | TIMESTAMP | 创建时间 |
| token_count | INTEGER | Token 数量 |

#### memo_message (备忘录表)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键 |
| original_session_id | INTEGER | 原会话 ID |
| original_message_id | INTEGER | 原消息 ID |
| content | TEXT | 备忘录内容 (JSON) |
| created_at | TIMESTAMP | 创建时间 |

#### resume_optimization (简历优化表)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键 |
| job_title | TEXT | 职位标题 |
| job_description | TEXT | 职位描述 |
| industry_analysis | TEXT | 行业分析 |
| optimized_resume | TEXT | 优化后的简历 |
| optimization_suggestions | TEXT | 优化建议 (JSON) |
| matching_analysis | TEXT | 匹配度分析 (JSON) |
| interview_preparation | TEXT | 面试准备 |
| created_at | TIMESTAMP | 创建时间 |

#### notes (笔记表)
| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 笔记标题 |
| content | TEXT | 笔记内容 |
| user_id | INTEGER | 用户 ID |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 4.5 前端路由

| 路径 | 组件 | 认证要求 | 描述 |
|------|------|---------|------|
| `/login` | LoginPage | 否 | 登录页面 |
| `/` | HomeView | 是 | 首页 |
| `/chat` | ChatPage | 是 | 聊天页面 |
| `/details` | DetailsPage | 是 | 会话详情 |
| `/memo` | MemoPage | 否 | 备忘录 |
| `/stats` | StatsPage | 是 | 数据统计 |
| `/resume` | ResumeOptimizer | 是 | 简历优化 |
| `/resume/list` | ResumeList | 是 | 简历列表 |
| `/notes` | NotesPage | 是 | 笔记管理 |

---

## 五、部署架构

### 5.1 Docker 部署

项目使用 Docker Compose 进行容器化部署:

```yaml
services:
  backend:
    image: crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/backend:latest
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
      - ./results:/app/results
    environment:
      - GLM_API_KEY=${GLM_API_KEY}
      - QWEN_API_KEY=${QWEN_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  frontend:
    image: crpi-76fbd77t4270ljs4.cn-hangzhou.personal.cr.aliyuncs.com/xueyang_me/frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 5.2 环境变量配置

**必需的环境变量**:
- `GLM_API_KEY` - 智谱 AI API 密钥
- `QWEN_API_KEY` - 通义千问 API 密钥
- `DEEPSEEK_API_KEY` - DeepSeek API 密钥
- `TAVILY_API_KEY` - Tavily 搜索 API 密钥
- `SECRET_KEY` - JWT 签名密钥

**可选的环境变量**:
- `GLM_API_BASE` - 智谱 AI API 基础 URL
- `QWEN_API_BASE` - 通义千问 API 基础 URL
- `DEEPSEEK_API_BASE` - DeepSeek API 基础 URL
- `LANGSMITH_TRACING` - LangSmith 追踪开关
- `LANGSMITH_API_KEY` - LangSmith API 密钥

### 5.3 部署目标

- **阿里云 ECS**: 47.110.67.241
- **容器镜像仓库**: 阿里云容器镜像服务 (杭州)

---

## 六、安全设计

### 6.1 认证安全
- JWT Token 认证，HS256 算法
- Token 存储于前端 localStorage
- 敏感 API 端点需要认证
- 公开端点白名单机制

### 6.2 数据安全
- SQLite 数据库文件存储于服务器
- 敏感配置通过环境变量管理
- CORS 跨域配置 (生产环境应限制具体域名)

### 6.3 建议的安全加固
1. 生产环境启用 HTTPS
2. 限制 CORS 允许的具体域名
3. 实现 Token 刷新机制
4. 添加 API 请求频率限制
5. 实现用户权限分级

---

## 七、性能优化

### 7.1 前端优化
- Vite 构建，支持 HMR 热更新
- 组件懒加载 (路由级别)
- 静态资源 CDN 加速 (可配置)

### 7.2 后端优化
- 异步 IO (FastAPI + Uvicorn)
- 数据库索引优化
- 流式响应减少首字延迟
- 上下文压缩减少 Token 消耗

### 7.3 数据库优化
- 关键字段建立索引
- 时间字段降序索引加速最新数据查询
- 外键约束保证数据一致性

---

## 八、开发工作流

### 8.1 CI/CD 流程

项目配置了 Gitee Pipeline:
- **分支流水线**: 功能分支开发
- **PR 流水线**: 代码审查
- **主分支流水线**: 自动构建和部署

### 8.2 本地开发

```bash
# 启动后端
cd backend
python main.py

# 启动前端
cd frontend
npm run dev
```

### 8.3 部署流程

```bash
# 本地构建并推送镜像
./deploy.sh

# 远程服务器部署
./deploy-to-server.sh
```

---

## 九、扩展性设计

### 9.1 多模型支持
- 通过 `MODEL_CONFIGS` 配置轻松添加新模型
- 支持任何 OpenAI 兼容 API 的模型

### 9.2 服务模块化
- API 路由按功能模块拆分
- 服务层独立，便于单元测试
- 数据库操作封装，便于迁移

### 9.3 未来扩展方向
1. 用户系统 (多用户支持)
2. 知识库管理 (RAG 检索增强)
3. 更多 AI 功能 (代码生成、翻译等)
4. 移动端应用
5. 实时协作功能

---

## 十、项目统计

- **总文件数**: 87 个
- **后端 API 模块**: 7 个
- **前端页面**: 9 个
- **数据库表**: 5 个
- **支持的大模型**: 3 个

---

## 附录

### A. 相关文档
- `README.md` - 项目说明
- `DEPLOYMENT.md` - 部署指南
- `REMOTE_DEPLOYMENT.md` - 远程部署指南
- `LOCAL_RUN_GUIDE.md` - 本地运行指南

### B. 联系方式
- 📧 邮箱: davindai@foxmail.com
- 🌐 Gitee: https://gitee.com/daihongtao111/xueyang

---

<div align="center">

**学氧助手** - 让学习像呼吸一样自然

*文档由 OpenClaw 自动生成 🔧*

</div>
