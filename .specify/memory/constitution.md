<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial ratification)
  Added sections:
    - Core Principles (5): Legacy Reuse First, Incremental Migration,
      Visitor-Scoped Data Isolation, Architectural Consistency, Simplicity First
    - Technology Stack Constraints
    - Development Workflow
    - Governance
  Removed sections: None (initial version)
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ aligned (Constitution Check section exists)
    - .specify/templates/spec-template.md ✅ aligned (scope/requirements section covers legacy context)
    - .specify/templates/tasks-template.md ✅ aligned (phase-based tasks fit incremental migration)
    - .specify/templates/checklist-template.md ✅ aligned (no constitution-specific changes needed)
  Follow-up TODOs: None
-->
# 学氧助手 (XueYang) 项目宪法

## 核心原则

### I. 存量复用优先 (Legacy Reuse First)

现有功能模块和架构设计是经过生产验证的资产。

- 新功能开发 MUST 优先复用已有模块（数据隔离模型、LLM 服务抽象、认证中间件），而非推倒重来。
- 只有在存量代码确实无法满足需求、且在 Spec 中明确说明了技术原因时，才允许替换。
- 禁止"为重构而重构"——没有功能增益的代码翻新不应排入开发计划。

**理由**: 避免为"新"而"新"。存量代码虽然可能在风格上不完美，但其行为是已知的、边界是明确的。重写意味着重新发现所有边界 case，ROI 往往为负。

### II. 渐进式迁移 (Incremental Migration)

旧页面的替换 MUST 采用渐进式策略，禁止大爆炸式重写（Big-Bang Rewrite）。

- 新实现 MUST 达到功能对等（Feature Parity）并经验证后，旧页面才可下线。
- 每替换一个页面就是一个可独立交付、可独立回滚的里程碑。
- 新旧页面可以并存于同一部署中，通过路由渐进切换。

**理由**: 存量项目最大的风险不是技术债，而是重写过程中丢失隐式需求和边界行为。渐进式迁移把风险摊到每一步，每一步都小到可以完整验证。

### III. 访客级数据隔离 (Visitor-Scoped Data Isolation)

每个用户/访客的数据 MUST 存储在独立隔离空间中（`backend/data/{visitor_id}/`）。

- SQLite 数据库、ChromaDB 向量库均按 visitor_id 路由，由 `db.py` 服务层统一管理。
- 任何新功能不得破坏或绕过此隔离模型。所有 CRUD 操作 MUST 以 visitor_id 为第一级范围限定。
- 登录用户与匿名访客使用相同的隔离机制，仅 visitor_id 来源不同（JWT username vs UUID）。

**理由**: 这是系统数据安全的基石。一次 SQL 注入或 Bug 只能影响单个用户的数据，无法横向扩散。

### IV. 架构一致性 (Architectural Consistency)

新功能 MUST 遵循现有架构模式，保持系统内聚性。

- LLM 调用：统一通过 `ChatOpenAI` 兼容抽象层（`app/services/llm.py`），不直接调用提供方 SDK。
- API 路由：使用 FastAPI Router 模式，在 `main.py` 中统一注册，响应遵循 snake_case 序列化。
- 认证：通过自定义中间件 `auth_middleware` 注入 `request.state.visitor_id`，不使用 FastAPI Depends。
- 前端：Vue 3 Composition API（`ref`/`reactive` + `setup`），不引入 Options API 新代码，不引入 Pinia。
- 配置：`.env` 管理敏感配置，禁止硬编码密钥、URL 或环境特定值。

除非有明确的技术理由并在 Spec 中充分论证，不得引入新的架构范式。

### V. 简洁优先 (Simplicity First)

YAGNI（You Aren't Gonna Need It）原则是最高优先级的设计约束。

- 不为"可能的需求"做设计预留、不引入当前不需要的抽象层。
- 技术选型优先内嵌方案（SQLite、ChromaDB）而非外部服务（PostgreSQL、Pinecone），直到规模确实需要。
- 自包含优于微服务：一个模块能做的事情，不拆成两个服务。
- 少即是多：状态管理用 Composition API + localStorage 而非 Pinia/Vuex；部署用单容器内嵌 nginx 而非独立 nginx 实例。

**理由**: 2C2G 的服务器上，每一层抽象都是真实资源消耗。简单的系统更容易理解、调试和迁移。

## 技术栈约束

| 层级 | 技术 | 约束 |
|------|------|------|
| 前端 | Vue 3 + Vite + Element Plus | 禁止引入新 UI 框架，禁止 Options API 新代码 |
| 后端 | Python + FastAPI + LangChain/LangGraph | LLM 编排的唯一方案 |
| 结构化存储 | SQLite（每用户独立 .db） | 禁止跨用户查询 |
| 向量存储 | ChromaDB（每用户独立 collection） | 内嵌运行，不独立部署 |
| LLM 提供方 | Zhipu GLM、Qwen、DeepSeek、Doubao | 统一通过 OpenAI 兼容层访问 |
| 部署 | Docker Compose + Nginx | SSL 终止在 Nginx 层，静态资源 gzip |
| 文档 | VitePress（`docs/` 子项目，npm workspaces） | 每个项目独立文档站 |
| CI/CD | Gitee Go → Alibaba Cloud CRPI | 自动构建 + 推送 |

## 开发工作流

### 新功能开发

1. **Spec 先行**: 在 `.specify/specs/` 下创建功能规格文档，明确目标、范围、验收标准
2. **Plan 拆解**: 基于 Spec 生成实施计划（plan.md），区分新建 vs 改造的范围
3. **Tasks 划分**: 拆解为独立可执行的任务，每个任务 < 一个会话的工作量
4. **增量实现**: 按 Task 顺序实现，完成后打勾

### 存量改造专项规则

当功能涉及替换旧页面/旧模块时，Spec 文档 MUST 额外包含：

- **改造动机**: 为什么旧实现不满足需求（功能缺失、性能瓶颈、维护成本）
- **新旧对比矩阵**: 旧页面功能清单 → 新页面覆盖情况
- **迁移策略**: 并轨运行期多长？如何验证功能对等？回滚方案是什么？
- **下线标准**: 旧页面可删除的条件（如：新页面稳定运行 N 天、所有流量已迁移）

### 部署流程

```
本地构建 → Docker 构建 → 推送 CRPI → ssh → docker compose pull → docker compose up -d
```

- 前端和文档必须一起构建后再打包镜像（`npm run build` + `npm run build:docs`）
- SSL 证书通过 volume 挂载，不打包进镜像
- 部署后验证三个域名：`xueyang.me`、`learn.xueyang.me`、`docs.xueyang.me`

## 治理

本宪法是学氧助手项目的最高开发准则。所有代码变更、架构决策、技术选型不得与之冲突。

### 修订流程

1. 提出修订动机，说明现有原则为何不适用
2. 在 Spec 文档中说明修订内容及影响范围
3. 修订后的宪法文本经审查批准
4. 同步更新相关模板和 `CODEBUDDY.md`

### 版本规则

语义化版本：`MAJOR.MINOR.PATCH`

- **MAJOR**: 原则删除或根本性重定义（向后不兼容）
- **MINOR**: 新增原则、新增章节、实质性扩展已有原则
- **PATCH**: 措辞澄清、格式修正、非语义性调整

### 合规检查

- 每个 Spec 对应的 plan.md MUST 包含 "Constitution Check" 章节，逐条验证是否符合宪法原则
- `CODEBUDDY.md` 作为宪法的运行时执行指南，AI 编码助手在开发时参考

**Version**: 1.0.0 | **Ratified**: 2026-07-30 | **Last Amended**: 2026-07-30
