from typing import List, Dict, Any, Optional
import logging
from app.services.db import (
    add_problem,
    get_problem,
    get_recent_problems,
    get_problem_by_difficulty,
    add_user_answer,
    get_user_answers,
    get_difficulty_stats
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodingPlaygroundService:
    def add_problem(self, visitor_id: str, title: str, description: str, difficulty: int, examples: List[Dict[str, Any]]) -> int:
        """添加题目"""
        return add_problem(visitor_id, title, description, difficulty, examples)
    
    def get_problem(self, visitor_id: str, problem_id: int) -> Optional[Dict[str, Any]]:
        """获取题目"""
        return get_problem(visitor_id, problem_id)
    
    def get_recent_problems(self, visitor_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的题目"""
        return get_recent_problems(visitor_id, limit)
    
    def get_problem_by_difficulty(self, visitor_id: str, difficulty: int) -> Optional[Dict[str, Any]]:
        """根据难度获取题目"""
        return get_problem_by_difficulty(visitor_id, difficulty)
    
    def add_user_answer(self, visitor_id: str, problem_id: int, user_code: str, evaluation_result: Dict[str, Any]) -> int:
        """添加用户答案"""
        return add_user_answer(visitor_id, problem_id, user_code, evaluation_result)
    
    def get_user_answers(self, visitor_id: str, problem_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户答案"""
        return get_user_answers(visitor_id, problem_id, limit)
    
    def get_difficulty_stats(self, visitor_id: str) -> Dict[int, int]:
        """获取难度统计"""
        return get_difficulty_stats(visitor_id)

# 创建全局编码操场服务实例
coding_playground_service = CodingPlaygroundService()
