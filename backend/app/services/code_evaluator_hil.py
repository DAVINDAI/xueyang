"""
LangGraph HIL (Human-in-the-Loop) 示例
======================================
场景：算法题代码评估，AI 给出修改建议后「暂停」，
     等用户确认是否接受，再继续执行。

HIL 三件套：
  1. MemorySaver checkpointer  —— 持久化 graph 状态，支持暂停/恢复
  2. interrupt()               —— 在节点内部挂起，把数据暴露给外部
  3. Command(resume=value)     —— 注入人类决策，graph 从断点继续
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command

from app.services.llm import llm_service

logger = logging.getLogger(__name__)


# ─────────────────────────── 状态定义 ────────────────────────────

class HilState(TypedDict):
    """贯穿整个 graph 的共享状态"""
    problem: Dict[str, Any]          # 题目信息
    user_code: str                   # 用户提交的原始代码
    analysis: Optional[str]          # LLM 分析结果（文字）
    suggested_fix: Optional[str]     # LLM 建议的修复代码
    human_approved: Optional[bool]   # 人类决策：True=接受 / False=拒绝
    final_code: str                  # 最终代码（接受修改后 or 原始代码）
    final_report: str                # 最终评估报告


# ─────────────────────────── 节点函数 ────────────────────────────

def analyze_code(state: HilState) -> Dict:
    """
    节点1：LLM 分析用户代码，生成问题描述和建议修复。
    这里是纯自动步骤，不需要人类介入。
    """
    logger.info("[HIL] 节点 analyze_code 开始...")

    problem = state["problem"]
    user_code = state["user_code"]

    prompt = f"""请分析以下算法题的代码，找出问题并给出修改建议。

题目：{problem.get("title", "")}
描述：{problem.get("description", "")}

用户代码：
```python
{user_code}
```

请按 JSON 格式输出，字段：
{{
  "has_issues": true/false,
  "analysis": "问题分析（中文，2-3句话）",
  "suggested_fix": "完整的修复代码（Python 代码字符串）"
}}
"""
    response = llm_service.generate_completion("qwen-plus", prompt)

    # 解析 LLM 输出
    result = _parse_json(response, {
        "has_issues": False,
        "analysis": "代码看起来没有明显问题。",
        "suggested_fix": user_code
    })

    logger.info(f"[HIL] 分析完成，有问题: {result['has_issues']}")

    return {
        "analysis": result["analysis"],
        "suggested_fix": result["suggested_fix"] if result["has_issues"] else None,
    }


def ask_human(state: HilState) -> Dict:
    """
    节点2：HIL 关键节点。
    调用 interrupt() 将控制权交还给调用方，graph 在此挂起。
    调用方（API 层）收到 InterruptedError，把 analysis 推给前端。
    用户点击「接受/拒绝」后，调用方用 Command(resume=...) 恢复。
    """
    logger.info("[HIL] 节点 ask_human —— 即将 interrupt，等待人类决策...")

    # ★ 核心：把需要展示给用户的信息通过 interrupt() 暴露出去
    #   interrupt() 会抛出异常挂起 graph，
    #   传入的值可被外部调用者捕获后转发给前端
    human_decision = interrupt({
        "type": "human_review",
        "analysis": state["analysis"],
        "suggested_fix": state.get("suggested_fix"),
        "original_code": state["user_code"],
        "message": "AI 检测到代码可能存在问题并给出了修复建议，是否接受？"
    })

    # 恢复后，human_decision 就是 Command(resume=value) 里的 value
    # 约定：True = 接受修改，False = 拒绝
    approved = bool(human_decision)
    logger.info(f"[HIL] 人类决策: {'接受' if approved else '拒绝'}")

    return {"human_approved": approved}


def apply_fix(state: HilState) -> Dict:
    """节点3a：用户接受修改，采用 LLM 建议的代码。"""
    logger.info("[HIL] 节点 apply_fix —— 用户接受了修改")
    return {"final_code": state["suggested_fix"] or state["user_code"]}


def keep_original(state: HilState) -> Dict:
    """节点3b：用户拒绝修改，保留原始代码。"""
    logger.info("[HIL] 节点 keep_original —— 用户拒绝修改，保留原代码")
    return {"final_code": state["user_code"]}


def generate_report(state: HilState) -> Dict:
    """节点4：基于最终代码生成评估报告。"""
    logger.info("[HIL] 节点 generate_report 开始...")

    approved = state.get("human_approved", False)
    decision_text = "用户接受了 AI 修改建议" if approved else "用户保留了原始代码"

    report = (
        f"## 代码评估报告\n\n"
        f"**AI 分析**：{state['analysis']}\n\n"
        f"**人类决策**：{decision_text}\n\n"
        f"**最终代码**：\n```python\n{state['final_code']}\n```"
    )

    return {"final_report": report}


# ─────────────────────────── 条件边 ────────────────────────────

def route_after_human(state: HilState) -> str:
    """根据人类决策选择下一个节点。"""
    if state.get("suggested_fix") and state.get("human_approved"):
        return "apply_fix"
    return "keep_original"


# ─────────────────────────── Graph 构建 ────────────────────────────

def build_hil_graph():
    """构建并编译 HIL graph。checkpointer 是暂停/恢复的关键。"""
    builder = StateGraph(HilState)

    builder.add_node("analyze_code", analyze_code)
    builder.add_node("ask_human", ask_human)
    builder.add_node("apply_fix", apply_fix)
    builder.add_node("keep_original", keep_original)
    builder.add_node("generate_report", generate_report)

    builder.set_entry_point("analyze_code")
    builder.add_edge("analyze_code", "ask_human")

    # ask_human 之后根据人类决策分叉
    builder.add_conditional_edges(
        "ask_human",
        route_after_human,
        {"apply_fix": "apply_fix", "keep_original": "keep_original"}
    )

    builder.add_edge("apply_fix", "generate_report")
    builder.add_edge("keep_original", "generate_report")
    builder.add_edge("generate_report", END)

    # ★ 必须传入 checkpointer，graph 才能在 interrupt 时持久化状态
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ─────────────────────────── 服务类 ────────────────────────────

class CodeEvaluatorHil:
    """
    HIL 代码评估服务。
    
    典型调用流程（配合 FastAPI）：
    
      1. POST /coding/hil/start
         → start_evaluation() → 返回 thread_id + interrupt_payload
         （graph 挂起在 ask_human 节点）
    
      2. 前端显示 AI 分析结果，用户点击「接受」或「拒绝」
    
      3. POST /coding/hil/resume  body: {thread_id, approved: true/false}
         → resume_evaluation() → 返回最终报告
         （graph 从断点继续，执行 apply_fix/keep_original → generate_report）
    """

    def __init__(self):
        self.graph = build_hil_graph()

    def start_evaluation(
        self, thread_id: str, problem: Dict[str, Any], user_code: str
    ) -> Dict[str, Any]:
        """
        第一阶段：启动 graph，执行到 interrupt 节点后挂起。
        返回给调用方的数据中包含 interrupt_payload，供前端展示。
        """
        config = {"configurable": {"thread_id": thread_id}}
        initial_state: HilState = {
            "problem": problem,
            "user_code": user_code,
            "analysis": None,
            "suggested_fix": None,
            "human_approved": None,
            "final_code": user_code,
            "final_report": "",
        }

        # 新版 LangGraph interrupt() 不抛异常，invoke 直接返回
        self.graph.invoke(initial_state, config)

        # 通过 get_state 检查是否在 interrupt 断点
        snapshot = self.graph.get_state(config)
        interrupts = snapshot.tasks[0].interrupts if snapshot.tasks else []

        executed_nodes = _extract_executed_nodes(self.graph.get_state_history(config))
        current_node = snapshot.next[0] if snapshot.next else "end"

        if interrupts:
            payload = interrupts[0].value
            logger.info(f"[HIL] graph 暂停，thread_id={thread_id}")
            return {
                "status": "waiting_for_human",
                "thread_id": thread_id,
                "interrupt_payload": payload,
                "current_node": current_node,
                "executed_nodes": executed_nodes,
            }

        # 没有 interrupt，说明图已跑完（理论上不会发生）
        final = snapshot.values
        return {
            "status": "completed",
            "report": final.get("final_report"),
            "current_node": "end",
            "executed_nodes": executed_nodes,
        }

    def resume_evaluation(
        self, thread_id: str, approved: bool
    ) -> Dict[str, Any]:
        """
        第二阶段：注入人类决策，graph 从断点继续执行直到结束。
        """
        config = {"configurable": {"thread_id": thread_id}}

        # ★ Command(resume=value) 是恢复 graph 的标准方式
        #   value 会成为 interrupt() 的返回值
        result = self.graph.invoke(Command(resume=approved), config)

        snapshot = self.graph.get_state(config)
        executed_nodes = _extract_executed_nodes(self.graph.get_state_history(config))

        logger.info(f"[HIL] graph 执行完毕，thread_id={thread_id}")
        return {
            "status": "completed",
            "human_approved": result.get("human_approved"),
            "final_code": result.get("final_code"),
            "final_report": result.get("final_report"),
            "current_node": "end",
            "executed_nodes": executed_nodes,
        }

    # ──────────────────── 流式版（SSE） ────────────────────

    async def start_evaluation_stream(
        self, thread_id: str, problem: Dict[str, Any], user_code: str
    ):
        """
        SSE 流式版：每完成一个节点就 yield 一个事件，
        遇到 interrupt 时 yield interrupt 事件后流结束。
        """
        config = {"configurable": {"thread_id": thread_id}}
        initial_state: HilState = {
            "problem": problem,
            "user_code": user_code,
            "analysis": None,
            "suggested_fix": None,
            "human_approved": None,
            "final_code": user_code,
            "final_report": "",
        }

        executed: list[str] = []

        # stream_mode="updates"：每完成一个节点就 yield 一次
        async for chunk in self.graph.astream(initial_state, config, stream_mode="updates"):
            for node_name in chunk:
                if node_name != "__start__":
                    executed.append(node_name)
                    yield {"type": "node", "node": node_name, "executed": executed}

        # astream 迭代结束 → 检查是 interrupt 还是跑完了
        snapshot = self.graph.get_state(config)
        interrupts = snapshot.tasks[0].interrupts if snapshot.tasks else []
        current_node = snapshot.next[0] if snapshot.next else "end"

        if interrupts:
            logger.info(f"[HIL] graph 暂停（流式），thread_id={thread_id}")
            yield {
                "type": "interrupt",
                "thread_id": thread_id,
                "current_node": current_node,
                "payload": interrupts[0].value,
                "executed_nodes": executed,
            }
        else:
            final = snapshot.values
            yield {
                "type": "done",
                "final_code": final.get("final_code", ""),
                "report": final.get("final_report", ""),
                "executed_nodes": executed,
            }

    async def resume_evaluation_stream(self, thread_id: str, approved: bool):
        """
        流式版 resume：从 checkpoint 继续，逐节点 yield，直到结束或再次 interrupt。
        """
        config = {"configurable": {"thread_id": thread_id}}

        executed: list[str] = []

        async for chunk in self.graph.astream(Command(resume=approved), config, stream_mode="updates"):
            for node_name in chunk:
                if node_name != "__start__":
                    executed.append(node_name)
                    yield {"type": "node", "node": node_name, "executed": executed}

        snapshot = self.graph.get_state(config)
        interrupts = snapshot.tasks[0].interrupts if snapshot.tasks else []

        if interrupts:
            yield {
                "type": "interrupt",
                "thread_id": thread_id,
                "current_node": snapshot.next[0] if snapshot.next else "end",
                "payload": interrupts[0].value,
                "executed_nodes": executed,
            }
        else:
            final = snapshot.values
            logger.info(f"[HIL] graph 流式执行完毕，thread_id={thread_id}")
            yield {
                "type": "done",
                "final_code": final.get("final_code", ""),
                "report": final.get("final_report", ""),
                "executed_nodes": executed,
            }


# ─────────────────────────── 工具函数 ────────────────────────────

def _extract_executed_nodes(state_history) -> list[str]:
    """
    从 get_state_history() 迭代器中提取已执行的节点列表（按执行顺序）。
    LangGraph 每个 checkpoint 的 metadata['writes'] 记录该步骤写入的节点名。
    history 是倒序的（最新在前），反转后得到执行顺序。
    """
    nodes = []
    for snapshot in state_history:
        writes = (snapshot.metadata or {}).get("writes") or {}
        for node_name in writes:
            if node_name not in nodes and node_name != "__start__":
                nodes.append(node_name)
    nodes.reverse()
    return nodes


def _parse_json(text: str, default: Dict) -> Dict:
    """从 LLM 输出中提取 JSON，失败返回 default。"""
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return default


# 全局单例
code_evaluator_hil = CodeEvaluatorHil()
