# AsyncGenerator：yield 和 await 是两套正交机制

## 起点

从 `code_evaluator_hil.py` 的 SSE 流式改造出发，沿着 `astream` 一路往下挖到 Python 异步生态的底层。

```python
async for chunk in self.graph.astream(initial_state, config, stream_mode="updates"):
    yield {"type": "node", "node": node_name, "executed": executed}
```

## 两条线

`async def` + `yield`（AsyncGenerator）是两条正交机制的交汇点：

### yield 线

**Generator → Iterator Protocol → 惰性求值 → 流式数据传递**

```python
def gen():
    yield 1  # 暂停，把 1 给调用方
    yield 2  # 调用方 next() 后继续，交出 2
```

- 同一个协程内部的**值传递**
- 不涉及事件循环
- 调用方通过 `__next__` / `__anext__` 恢复

### await 线

**Coroutine → Event Loop → 非阻塞 IO → 并发调度**

```python
result = await call_llm()  # 暂停，控制权还给事件循环
```

- 涉及**事件循环调度**
- 等 Future 就绪后由事件循环回调恢复
- 其他协程可以在此期间执行

## 对比

| | yield | await |
|---|---|---|
| 暂停目标 | 把值给调用方 | 把控制权还给事件循环 |
| 恢复者 | 调用方调 `__anext__` | 事件循环回调 |
| 涉及层 | 同一协程内部 | 跨协程调度 |
| 用时 | LLM 生成完一串后给结果 | LLM 一个字还没返回，等着 |

## async for 的底层

```python
# 语法糖
async for x in async_gen:
    ...

# 展开等价于
it = async_gen.__aiter__()
while True:
    try:
        x = await it.__anext__()  # ← 关键：await
    except StopAsyncIteration:
        break
    ...
```

每次 `__anext__()` 返回一个 awaitable，`await` 允许事件循环在等的时候去干别的，拿到值后继续循环体。迭代本身是**串行的**——不拿到 chunk1 就不会去拿 chunk2。

## BSP + AsyncGenerator

LangGraph 底层用 Pregel/BSP 模型执行图：

```
loop:
  1. plan   → 找出"入边已就绪"的节点
  2. exec   → 并发执行同一超步的节点（asyncio.gather）
  3. yield  → astream 把 chunk 推出去
  4. goto 1 → 直到无节点可执行或遇到 interrupt
```

`interrupt()` 不抛异常，它标记当前节点为 suspended，循环检测到后退出。超步没执行完的节点不会出现在 chunk 里。

## 时间线（两层生成器嵌套）

```python
# 内层 astream
chunk = await loop.step()  # ③ 真正阻塞：等 LLM 返回
yield chunk                 # ④ 内层交出 chunk

# 外层 start_evaluation_stream
async for chunk in ...:     # ① 拿到 chunk
    yield {"type": "node"}  # ② 外层交出 SSE 事件
```

## Python 生态中的常见模式

只要数据不是一次性全部就绪，`async def` + `yield` 就是标准答案：

| 场景 | 用法 |
|---|---|
| FastAPI SSE | `StreamingResponse(event_gen())` |
| LangChain | `async for chunk in chain.astream(...)` |
| OpenAI SDK | `async for event in client.chat.completions.create(stream=True)` |
| SQLAlchemy async | `async for row in session.execute(...)` |
| aiofiles | `async for line in aiofiles.open("big.log")` |

## 推导链（自底向上）

```
代码改造：SSE 流式 HIL 评估
    ↓
astream 怎么做到逐节点推送？
    ↓
Pregel/BSP 超步模型
    ↓
async for 语法糖展开
    ↓
await __anext__() — 协程调度
    ↓
yield vs await 两条正交线
```
