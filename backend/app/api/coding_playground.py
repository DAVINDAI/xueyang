from fastapi import APIRouter, HTTPException, Body, Request
from typing import Dict, Any
import logging
import uuid
from app.services.coding_playground import coding_playground_service
from app.services.problem_generator import problem_generator_service
from app.services.code_evaluator_pro import code_evaluator_service_pro as code_evaluator_service
from app.services.code_evaluator_hil import code_evaluator_hil
from app.exceptions import BusinessException, SystemException, ValidationException, ErrorCode

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coding-playground", tags=["coding_playground"])

@router.get("/problem")
async def get_problem(request: Request, difficulty: int = 1) -> Dict[str, Any]:
    """获取算法题目"""
    try:
        # 获取visitor_id
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 验证难度参数
        if difficulty not in [1, 2, 3]:
            difficulty = 1
        
        # 尝试获取已有的题目
        problem = coding_playground_service.get_problem_by_difficulty(visitor_id, difficulty)
        
        # 如果没有对应难度的题目，生成新题目
        if not problem:
            problem = problem_generator_service.generate_problem(difficulty, visitor_id)
            # 保存生成的题目
            coding_playground_service.add_problem(
                visitor_id=visitor_id,
                title=problem["title"],
                description=problem["description"],
                difficulty=problem["difficulty"],
                examples=problem["examples"]
            )
        
        return {
            "success": True,
            "problem": problem
        }
    except Exception as e:
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"获取题目失败: {str(e)}")

@router.post("/submit")
async def submit_code(
    request: Request,
    problem_id: int = Body(...),
    code: str = Body(...)
) -> Dict[str, Any]:
    """提交代码进行评估"""
    try:
        # 获取visitor_id
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 获取题目
        problem = coding_playground_service.get_problem(visitor_id, problem_id)
        if not problem:
            raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "题目不存在")
        
        # 评估代码
        evaluation = code_evaluator_service.evaluate_code(problem, code)
        
        # 保存用户答案
        coding_playground_service.add_user_answer(
            visitor_id=visitor_id,
            problem_id=problem_id,
            user_code=code,
            evaluation_result=evaluation
        )
        
        return {
            "success": True,
            "evaluation": evaluation
        }
    except Exception as e:
        if isinstance(e, (BusinessException, SystemException, ValidationException)):
            raise
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"评估代码失败: {str(e)}")

@router.get("/stats")
async def get_stats(request: Request) -> Dict[str, Any]:
    """获取统计信息"""
    try:
        # 获取visitor_id
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        stats = coding_playground_service.get_difficulty_stats(visitor_id)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"获取统计信息失败: {str(e)}")

@router.get("/answers/{problem_id}")
async def get_user_answers(request: Request, problem_id: int) -> Dict[str, Any]:
    """获取用户答题历史"""
    try:
        # 获取visitor_id
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        answers = coding_playground_service.get_user_answers(visitor_id, problem_id)
        return {
            "success": True,
            "answers": answers
        }
    except Exception as e:
        logger.error(f"获取答题历史失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"获取答题历史失败: {str(e)}")


# ─────────────────────────── HIL 端点 ────────────────────────────

@router.post("/hil/start")
async def hil_start(
    request: Request,
    problem_id: int = Body(...),
    code: str = Body(...)
) -> Dict[str, Any]:
    """
    HIL 第一阶段：启动 LangGraph，执行到 interrupt 节点后挂起。
    返回 thread_id 和 AI 分析结果，前端凭 thread_id 发起第二阶段。
    """
    try:
        visitor_id = getattr(request.state, "visitor_id", None)
        problem = coding_playground_service.get_problem(visitor_id, problem_id)
        if not problem:
            raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "题目不存在")

        thread_id = f"{visitor_id}-{uuid.uuid4().hex[:8]}"
        result = code_evaluator_hil.start_evaluation(thread_id, problem, code)
        return {"success": True, **result}

    except Exception as e:
        if isinstance(e, (BusinessException, SystemException, ValidationException)):
            raise
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"HIL 启动失败: {str(e)}")


@router.post("/hil/resume")
async def hil_resume(
    thread_id: str = Body(...),
    approved: bool = Body(...)
) -> Dict[str, Any]:
    """
    HIL 第二阶段：用户做出决策（接受/拒绝 AI 修改），graph 从断点继续。
    approved=true  → 采用 AI 修复代码
    approved=false → 保留用户原代码
    """
    try:
        result = code_evaluator_hil.resume_evaluation(thread_id, approved)
        return {"success": True, **result}

    except Exception as e:
        if isinstance(e, (BusinessException, SystemException, ValidationException)):
            raise
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"HIL 恢复失败: {str(e)}")