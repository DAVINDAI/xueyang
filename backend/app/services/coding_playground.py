from typing import List, Dict, Any, Optional
import sqlite3
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodingPlaygroundService:
    def __init__(self, db_path: str = "./data/coding_playground.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建题目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty INTEGER NOT NULL,  -- 1: 简单, 2: 中等, 3: 困难
            examples TEXT NOT NULL,  -- JSON格式存储示例输入输出
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建用户答案表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            user_code TEXT NOT NULL,
            evaluation_result TEXT NOT NULL,  -- JSON格式存储评估结果
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_problem(self, title: str, description: str, difficulty: int, examples: List[Dict[str, Any]]) -> int:
        """添加题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        examples_json = json.dumps(examples)
        cursor.execute(
            "INSERT INTO problems (title, description, difficulty, examples) VALUES (?, ?, ?, ?)",
            (title, description, difficulty, examples_json)
        )
        
        problem_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return problem_id
    
    def get_problem(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """获取题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "examples": json.loads(row[4]),
                "created_at": row[5]
            }
        return None
    
    def get_recent_problems(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM problems ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        conn.close()
        
        problems = []
        for row in rows:
            problems.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "examples": json.loads(row[4]),
                "created_at": row[5]
            })
        
        return problems
    
    def get_problem_by_difficulty(self, difficulty: int) -> Optional[Dict[str, Any]]:
        """根据难度获取题目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM problems WHERE difficulty = ? ORDER BY ID LIMIT 1", (difficulty,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "examples": json.loads(row[4]),
                "created_at": row[5]
            }
        return None
    
    def add_user_answer(self, problem_id: int, user_code: str, evaluation_result: Dict[str, Any]) -> int:
        """添加用户答案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        evaluation_json = json.dumps(evaluation_result)
        cursor.execute(
            "INSERT INTO user_answers (problem_id, user_code, evaluation_result) VALUES (?, ?, ?)",
            (problem_id, user_code, evaluation_json)
        )
        
        answer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return answer_id
    
    def get_user_answers(self, problem_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户答案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM user_answers WHERE problem_id = ? ORDER BY created_at DESC LIMIT ?",
            (problem_id, limit)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        answers = []
        for row in rows:
            answers.append({
                "id": row[0],
                "problem_id": row[1],
                "user_code": row[2],
                "evaluation_result": json.loads(row[3]),
                "created_at": row[4]
            })
        
        return answers
    
    def get_difficulty_stats(self) -> Dict[int, int]:
        """获取难度统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT difficulty, COUNT(*) FROM problems GROUP BY difficulty")
        rows = cursor.fetchall()
        
        conn.close()
        
        stats = {1: 0, 2: 0, 3: 0}
        for row in rows:
            stats[row[0]] = row[1]
        
        return stats

# 创建全局编码操场服务实例
coding_playground_service = CodingPlaygroundService()
