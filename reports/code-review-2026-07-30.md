# 学氧助手代码审查报告

> 2026-07-30 · 全量静态审查，不动代码，只记录问题

---

## 高危问题

### 1. `api.js` — 响应拦截器破坏 axios 响应结构
**文件：** `frontend/src/api/api.js:78-85`

```js
api.interceptors.response.use(
  response => {
    if (response.data && typeof response.data === 'object') {
      return convertObjectKeys(response.data, snakeToCamel)
    }
    return response.data
  },
)
```

标准 axios 拦截器应返回 `response` 对象，这里直接返回了 `response.data`。调用方无法访问 `response.status`、`response.headers`。目前碰巧能工作（因为 `convertObjectKeys` 把 `access_token` → `accessToken`，调用方 `response.accessToken` 恰好对应 `response.data.accessToken`），但这是脆弱的巧合，不是可靠设计。

---

### 2. `ChatPage.vue` — SSE 完成后 `loadMessages()` 完全覆盖本地消息
**文件：** `frontend/src/views/ChatPage.vue:630-643`

SSE 流式完成的回调中调用 `await loadMessages()`，它执行 `messages.value = data`，完全替换本地消息列表。流式渲染的内容 → 服务端返回数据之间存在视觉跳跃。更关键的是：如果服务端数据与本地流式内容有任何不一致（时机差异、格式差异），用户会看到内容闪变。

---

### 3. `code_evaluator_pro.py` — `_run_code_locally` 和 `_analyze_performance` 是空桩
**文件：** `backend/app/services/code_evaluator_pro.py`

LangGraph 调试循环的核心两步——在本地执行代码、分析性能——是 stub 实现。整个「生成修复 → 本地执行 → 条件循环」链路上缺少最关键的反馈环节。LLM 生成的修复代码没有被真正验证过，缺少执行结果作为下一轮迭代的输入。

---

### 4. `visitor_manager.py` — 无并发锁保护，多协程数据竞争
**文件：** `backend/app/services/visitor_manager.py`

```python
def update_visitor(self, visitor_id: str):
    self.visitor_data[visitor_id] = {'last_access': current_time}
    self._cleanup_visitors()        # 遍历字典同时可能被其他协程修改
    self._save_visitor_data()       # 多协程同时 json.dump → 文件损坏
```

没有 `threading.Lock` 或 `asyncio.Lock`。在 FastAPI async 下，多个协程可能同时修改 `visitor_data` 字典和写入 JSON 文件。每次访问都触发一次完整文件 I/O 也是性能隐患。

---

### 5. `scheduler.py` — async 函数跑在线程池 + 相对路径 SQLite
**文件：** `backend/app/services/scheduler.py:19,48,82-88`

两个独立问题：
- `SQLAlchemyJobStore(url='sqlite:///jobs.db')` — 相对路径，当前工作目录改变会导致 job 数据丢失
- async 函数被 APScheduler 的 `ThreadPoolExecutor` 执行，`await` 行为未定义
- `asyncio.create_task()` 在没有事件循环的线程中调用会直接报错

---

### 6. `migrate.py` — 异常静默吞噬 + executescript 无事务原子性
**文件：** `backend/database/migrate.py`

```python
except Exception as e:
    print(f"数据库迁移失败: {e}")
```

迁移失败后脚本正常退出（exit code 0），`docker-entrypoint.sh` 无法感知，容器会带着坏数据库继续启动。`executescript` 会自动在每条语句后 commit，意味着多语句脚本中途失败后前面的修改无法回滚。

---

### 7. `llamaindex_service.py` — 全局 `Settings.embed_model` 突变
**文件：** `backend/app/services/llamaindex_service.py`

调用 `Settings.embed_model = ...` 直接修改 LlamaIndex 的全局配置。如果以后有多个使用不同 embedding 模型的模块，会相互覆盖。

---

## 中危问题

### 前端

| # | 文件 | 行号 | 问题 |
|---|------|------|------|
| M1 | `CodingPlayground.vue` | 50-55 | `understandSummary` 收集用户输入但从未使用，功能不完整 |
| M2 | `CodingPlayground.vue` | 8,13 | 难度选择器和刷新按钮无防重复提交保护，快速操作可能并发调用 |
| M3 | `ChatPage.vue` | 257+748 | `loadSessions()` 在 `onMounted` 中被调用两次，重复网络请求 |
| M4 | `ChatPage.vue` | 153 | `@keyup.enter` 在中文 IME 选词时可能误触发发送 |
| M5 | `ChatPage.vue` | 644-657 | SSE 错误回调和外层 try-catch 双重处理错误 |
| M6 | `DetailsPage.vue` | 256-273 | `confirmRename` 缺少 `.trim()` 检查，允许纯空格名称 |
| M7 | `App.vue` | 56-57 | `loginStatus` + `isUserLoggedIn` 冗余中间状态，可能在某个更新点遗漏 |

### 后端

| # | 文件 | 问题 |
|---|------|------|
| M8 | `code_evaluator_pro.py` | `max_debug_attempts = 2`，注释说 5，不一致 |
| M9 | `code_evaluator_hil.py` | 过度宽泛的异常捕获，分支判断依赖脆弱的中断检测 |
| M10 | `llamaindex_service.py` | 回退索引与 ChromaDB 未连接；无界服务缓存 |

### 部署/配置

| # | 文件 | 问题 |
|---|------|------|
| M11 | `nginx.conf` | 生产环境暴露 `/docs` 和 `/redoc` API 文档 |
| M12 | `docker-compose.prod.yml` | healthcheck `retries=300`（2.5 小时），掩盖启动失败 |
| M13 | `migrate.py` vs compose | 数据库文件名不一致：`xueyang.db` vs `langgraph_data.db` |
| M14 | `nginx.conf` | `proxy_pass http://127.0.0.1:8000` 硬编码 IP |
| M15 | `stop.sh` | 仅通过 PID 文件查找，无法停止无 PID 文件残留进程 |
| M16 | `visitor_manager.py` | 每次 `update_visitor` 触发完整 JSON 写入，高并发 I/O 瓶颈 |

---

## 低危问题

| # | 领域 | 文件 | 问题 |
|---|------|------|------|
| L1 | 前端 | `api.js:94` | 401 使用 `window.location.href` 硬跳转，非 Vue Router |
| L2 | 前端 | `api.js:28-29` | `camelToSnake` 对连续大写（如 `APIKey`）转换错误 |
| L3 | 前端 | `ChatPage.vue:728` | Token 计数用字符串长度代替，中文不准确 |
| L4 | 前端 | `DetailsPage.vue:437` | `import { ElMessage }` 放在文件底部而非顶部 |
| L5 | 前端 | `CodingPlayground.vue:65` | 提示文本仅在用户输入后才显示，逻辑不够顺 |
| L6 | 前端 | `App.vue:60-70` | `getUsername` 解析失败仅 console.error，不清空 username |
| L7 | 后端 | `problem_generator.py` | LLM prompt 较简单，未要求边界条件和测试用例 |
| L8 | 后端 | `coding_playground.py` | 服务层纯透传，缺少输入校验 |
| L9 | 后端 | 多个文件 | 反复调用 `logging.basicConfig()`；`import json` 写在函数内 |
| L10 | 后端 | `scheduler.py` | `pause_job`/`resume_job` 对不存在的 job 静默无操作 |
| L11 | 部署 | `start.sh` | 端口检测与实际启动之间有时间窗口竞态 |
| L12 | 部署 | `start.sh` | 依赖 `lsof` 但未检查是否安装 |
| L13 | 部署 | `docker-compose.yml` | 挂载源码目录到容器（开发配置混入通用 compose） |
| L14 | 部署 | compose 文件 | `SECRET_KEY` 无默认值/必填校验，缺了也能启动 |

---

## 总结

| 类别 | 高危 | 中危 | 低危 |
|------|------|------|------|
| 前端 | 2 | 7 | 6 |
| 后端 | 3 | 4 | 5 |
| 部署 | 2 | 5 | 3 |
| **合计** | **7** | **16** | **14** |

**Top 5 最值得优先看的问题：**

1. `code_evaluator_pro.py` — 核心调试链路是空桩（功能缺陷）
2. `api.js` — 响应拦截器破坏 axios 结构（架构隐患）
3. `visitor_manager.py` — 并发安全 + I/O 瓶颈（稳定性隐患）
4. `migrate.py` — 迁移失败不阻止启动（运维风险）
5. `ChatPage.vue` — SSE 完成后覆盖本地消息（用户体验缺陷）
