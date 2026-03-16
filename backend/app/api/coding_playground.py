from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from app.services.coding_playground import coding_playground_service
from app.services.problem_generator import problem_generator_service
from app.services.code_evaluator_pro import code_evaluator_service_pro as code_evaluator_service

router = APIRouter(prefix="/coding-playground", tags=["coding_playground"])

@router.get("/problem")
async def get_problem(difficulty: int = 1) -> Dict[str, Any]:
    """获取算法题目"""
    try:
        # 验证难度参数
        if difficulty not in [1, 2, 3]:
            difficulty = 1
        
        # 尝试获取已有的题目
        problem = coding_playground_service.get_problem_by_difficulty(difficulty)
        
        # 如果没有对应难度的题目，生成新题目
        if not problem:
            problem = problem_generator_service.generate_problem(difficulty)
        
        return {
            "success": True,
            "problem": problem
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")

@router.post("/submit")
async def submit_code(
    problem_id: int = Body(...),
    code: str = Body(...)
) -> Dict[str, Any]:
    """提交代码进行评估"""
    try:
        # 获取题目
        problem = coding_playground_service.get_problem(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="题目不存在")
        
        # 评估代码
        evaluation = code_evaluator_service.evaluate_code(problem, code)
        
        # 保存用户答案
        coding_playground_service.add_user_answer(
            problem_id=problem_id,
            user_code=code,
            evaluation_result=evaluation
        )
        
        return {
            "success": True,
            "evaluation": evaluation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估代码失败: {str(e)}")

@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """获取统计信息"""
    try:
        stats = coding_playground_service.get_difficulty_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/answers/{problem_id}")
async def get_user_answers(problem_id: int) -> Dict[str, Any]:
    """获取用户答题历史"""
    try:
        answers = coding_playground_service.get_user_answers(problem_id)
        return {
            "success": True,
            "answers": answers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取答题历史失败: {str(e)}")