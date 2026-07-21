# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## Project Overview

**学氧助手 (XueYang)** — AI-powered learning assistant platform. A full-stack application with a Vue 3 frontend and Python FastAPI backend, using LangChain/LangGraph for LLM orchestration, SQLite for structured storage, and ChromaDB for vector search.

## Essential Commands

### Local Development

```bash
# Start everything (backend on :8000, frontend on :5173)
bash scripts/start.sh

# Stop everything
bash scripts/stop.sh

# Restart everything
bash scripts/restart.sh
```

`scripts/start.sh` auto-activates the Python venv, installs dependencies if missing, starts uvicorn with hot-reload, then starts Vite dev server. It logs PIDs so `stop.sh` can cleanly kill them.

### Backend Only

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend requires these environment variables in `.env`: `SECRET_KEY`, `GLM_API_KEY`, `QWEN_API_KEY`, `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, `TAVILY_API_KEY`. Optionally `LANGSMITH_API_KEY` for tracing.

### Frontend Only

```bash
cd frontend
npm install
npm run dev    # starts on :5173, expects backend at localhost:8000
```

### Docker Deployment

```bash
# Local Docker (uses docker-compose.yml)
bash docker-deploy-local.sh

# Production server (uses docker-compose.prod.yml, requires Alibaba Cloud registry login)
bash docker-deploy-server.sh
```

Production compose file adds SSL certs, health checks, and VPC-internal image registry. `docker-deploy-server.sh` auto-logs into the registry, backs up data, deploys, and prunes old images.

### Database Migration

Migrations run automatically via `backend/docker-entrypoint.sh` on container start (`python database/migrate.py`). Migration SQL files live in `backend/database/migrations/`. The script is idempotent.

## Architecture

### Backend (`backend/`)

**Entry point**: `main.py` — Creates the FastAPI app, registers middleware, includes all 14 API routers, and wires up startup/shutdown events.

**Custom auth middleware** (not FastAPI dependency injection): Every request passes through `auth_middleware` in `main.py`. It checks for a JWT Bearer token; if valid, sets `request.state.user` and `request.state.visitor_id` to the username. If no token, it falls back to `X-Visitor-ID` header or generates a temp UUID. This means the visitor ID is available to all downstream routes and services without explicit dependency injection.

**Data isolation model**: Each visitor/user gets their own isolated storage under `backend/data/{visitor_id}/` — a separate SQLite database (`langgraph_data.db`), a ChromaDB vector store, and for coding playground, `coding_playground.db`. The `db.py` service layer uses `get_db_connection(visitor_id)` to route to the correct database. This is the cornerstone of the entire system — every CRUD operation is scoped by visitor_id.

**LLM service** (`app/services/llm.py`): Wraps LangChain's `ChatOpenAI` to support four models configured in `app/config/__init__.py` — GLM-5 (1M context), Qwen-Plus (200K), DeepSeek-Chat (128K), and Doubao-Seed (128K). Each has its own API base and key env var. The service uses LCEL chains (`ChatPromptTemplate` → `ChatOpenAI` → `StrOutputParser`) for both streaming and non-streaming modes. Context compression triggers at 80% of model context length via `tokenizer.py`.

**Chat flow** (`app/api/chat.py`): Sessions and messages CRUD. The key endpoint is `/chat/completion/stream` which returns SSE. It loads conversation history from the visitor's SQLite, compresses if needed, streams via LangChain's `.astream()`, saves the full response, and asynchronously updates the ChromaDB vector index for semantic search.

**Search** (`app/api/search.py`): Three-way parallel search — LlamaIndex semantic search over ChromaDB embeddings, local SQLite full-text search on chat messages, and Tavily web search. Results are merged.

**Other notable API modules**:
- `resume.py` — PDF upload (PyMuPDF4LLM), LLM-powered analysis covering industry fit, match scoring, and interview preparation
- `coding_playground.py` — LLM-generated algorithm problems, code submission with evaluation via LangGraph (`code_evaluator_pro.py`) or a simpler evaluator
- `law.py` — Legal document RAG: Playwright-scraped Chinese legal documents indexed in `chroma_law/`, served via semantic search and RAG Q&A
- `notes.py` — Markdown note CRUD
- `assistant.py` / `communication.py` — Goal/task management and message polishing features
- `scheduler.py` — APScheduler-backed cron job management, persistence in `jobs.db`
- `prompts.py` — Prompt template management with LangSmith hub integration
- `parse.py` — NLP-based input routing to determine which page a user's query targets

**Exception handling**: Custom exception hierarchy in `app/exceptions.py` — `BusinessException`, `SystemException`, `ValidationException` — each with error codes. Global handlers in `main.py` catch both custom exceptions and unexpected errors.

**Memory**: `app/services/memory.py` uses LangChain's `InMemoryChatMessageHistory` with a size cap. Conversation history is loaded from SQLite on each request, not from this in-memory store — it serves as a runtime cache only.

### Frontend (`frontend/`)

**Entry point**: `src/main.js` — creates the Vue app with Element Plus, Vue Router (history mode), and globally mounts `$echarts`.

**No state management library**: The project uses Vue 3 Composition API (`ref`/`reactive`) plus `localStorage` for token and visitor ID. Login state is managed in `App.vue` by parsing the JWT payload on mount and watching route changes.

**API layer** (`src/api/api.js`): Axios instance with request interceptor that converts camelCase → snake_case for outgoing JSON and response interceptor that reverses the conversion. If logged in, it attaches `Authorization: Bearer` header; otherwise, it sends `X-Visitor-ID` from localStorage. On 401 responses, it auto-clears the token and redirects to `/login`.

**SSE streaming** (`ChatPage.vue`): Does NOT use Axios. Uses native `fetch` with `ReadableStream` to parse SSE `data:` events. This bypasses the axios interceptors and handles chunk-by-chunk rendering with Markdown, code highlighting (highlight.js), and Mermaid diagram rendering.

**12 routes**: Home (`/`), Login (`/login`), Chat (`/chat`), Coding Playground, Notes (list + detail), Memo, Resume (optimizer + history list), Details (statistics with ECharts), Law, Assistant, Communication. All routes except Home and Login are lazy-loaded. The router has a basic guard that redirects logged-in users from `/login` to `/`.

**Key pages**:
- `ChatPage.vue` — Multi-session management, model switching, SSE chat, Markdown rendering with code highlighting and Mermaid support, token counting
- `DetailsPage.vue` — ECharts pie chart (model usage distribution), line chart (daily message count), session detail drill-down
- `CommunicationPage.vue` / `AssistantPage.vue` — Written in Options API (the rest use Composition API)

### Data Flow Pattern

1. Frontend sends request with `Authorization` (logged-in) or `X-Visitor-ID` (anonymous)
2. `auth_middleware` in `main.py` sets `request.state.visitor_id`
3. API route extracts `visitor_id` from `request.state` (via `getattr(request.state, "visitor_id", None)`)
4. Service layer (`db.py`, `llamaindex_service.py`) uses `visitor_id` to route to the correct SQLite database and ChromaDB collection
5. Response flows back through the conversion layers (snake_case on wire, camelCase in frontend)

### Docker & Deployment

**Two compose files**: `docker-compose.yml` (local/generic, mounts backend source code for development) and `docker-compose.prod.yml` (production, SSL certs at :443, no source mount, health checks with `condition: service_healthy`).

**Images** are built and pushed to Alibaba Cloud Container Registry (CRPI). `backend/build.sh` uses a three-stage Docker build (base → deps → final) for layer caching. `frontend/build.sh` uses a multi-stage build (Node build → Nginx serve).

**CI/CD** via Gitee Go: four stages — Docker build, Python packaging, release upload, and host deployment to a specific server.

### Key Architectural Decisions

- **SQLite per user instead of a single PostgreSQL**: Simpler deployment, no external DB dependency, natural data isolation. Scale limits are acknowledged but acceptable for current usage.
- **ChromaDB for vector storage over Pinecone/Weaviate**: Embedded, no external service, pairs naturally with the per-user directory layout.
- **OpenAI-compatible API abstraction**: All four LLM providers (Zhipu GLM, Qwen, DeepSeek, Doubao) are accessed through the same `ChatOpenAI` LangChain class, just with different `api_base` URLs. This keeps the LLM service uniform.
- **Custom middleware over FastAPI dependencies for auth**: Ensures every request (including those that don't declare Depends) has a visitor_id set. Critical for the visitor-based data isolation to work everywhere without opt-in.
- **No Pinia/Vuex**: The app's state is simple enough (essentially just login status + current visitor ID) that Composition API with localStorage suffices.
- **LangSmith for prompt management**: Prompts can be pushed/pulled to LangSmith Hub, enabling prompt versioning and collaborative iteration without code changes.
