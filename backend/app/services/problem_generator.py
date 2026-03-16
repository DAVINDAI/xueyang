from typing import List, Dict, Any
import logging
from app.services.llm import llm_service
from app.services.coding_playground import coding_playground_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProblemGeneratorService:
    def __init__(self):
        self.model_name = "qwen-plus"  # 使用qwen大模型
    
    def generate_problem(self, difficulty: int) -> Dict[str, Any]:
        """生成算法题目"""
        try:
            # 获取最近的题目作为参考
            recent_problems = coding_playground_service.get_recent_problems(limit=5)
            
            # 构建提示词
            prompt = self._build_prompt(difficulty, recent_problems)
            
            # 调用大模型生成题目
            response = llm_service.generate_completion(self.model_name, prompt)
            
            # 解析生成的题目
            problem = self._parse_problem(response, difficulty)
            
            # 保存到数据库
            problem_id = coding_playground_service.add_problem(
                title=problem["title"],
                description=problem["description"],
                difficulty=problem["difficulty"],
                examples=problem["examples"]
            )
            
            problem["id"] = problem_id
            return problem
        except Exception as e:
            logger.error(f"生成题目失败: {e}")
            # 返回默认题目
            return self._get_default_problem(difficulty)
    
    def _build_prompt(self, difficulty: int, recent_problems: List[Dict[str, Any]]) -> str:
        """构建提示词"""
        difficulty_map = {
            1: "简单",
            2: "中等",
            3: "困难"
        }
        
        prompt = f"请生成一个{difficulty_map[difficulty]}难度的算法面试题目，要求如下：\n"
        prompt += "1. 题目需要有明确的描述和要求\n"
        prompt += "2. 提供至少2个示例输入和输出\n"
        prompt += "3. 题目应该是经典的算法问题\n"
        prompt += "4. 避免与以下已有题目重复：\n"
        
        for problem in recent_problems:
            prompt += f"   - {problem['title']}\n"
        
        prompt += "\n请按照以下JSON格式输出题目：\n"
        prompt += "{\n"
        prompt += "  \"title\": \"题目名称\",\n"
        prompt += "  \"description\": \"题目描述\",\n"
        prompt += "  \"examples\": [\n"
        prompt += "    {\n"
        prompt += "      \"input\": \"输入示例\",\n"
        prompt += "      \"output\": \"输出示例\"\n"
        prompt += "    }\n"
        prompt += "  ]\n"
        prompt += "}\n"
        
        return prompt
    
    def _parse_problem(self, response: str, difficulty: int) -> Dict[str, Any]:
        """解析生成的题目"""
        import json
        
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                problem = json.loads(json_str)
                problem["difficulty"] = difficulty
                return problem
        except Exception as e:
            logger.error(f"解析题目失败: {e}")
        
        # 解析失败，返回默认题目
        return self._get_default_problem(difficulty)
    
    def _get_default_problem(self, difficulty: int) -> Dict[str, Any]:
        """获取默认题目"""
        default_problems = {
            1: {
                "title": "两数之和",
                "description": "给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那 两个 整数，并返回他们的数组下标。",
                "difficulty": 1,
                "examples": [
                    {
                        "input": "nums = [2, 7, 11, 15], target = 9",
                        "output": "[0, 1]"
                    },
                    {
                        "input": "nums = [3, 2, 4], target = 6",
                        "output": "[1, 2]"
                    }
                ]
            },
            2: {
                "title": "反转链表",
                "description": "给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。",
                "difficulty": 2,
                "examples": [
                    {
                        "input": "head = [1,2,3,4,5]",
                        "output": "[5,4,3,2,1]"
                    },
                    {
                        "input": "head = [1,2]",
                        "output": "[2,1]"
                    }
                ]
            },
            3: {
                "title": "接雨水",
                "description": "给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。",
                "difficulty": 3,
                "examples": [
                    {
                        "input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]",
                        "output": "6"
                    },
                    {
                        "input": "height = [4,2,0,3,2,5]",
                        "output": "9"
                    }
                ]
            }
        }
        
        return default_problems.get(difficulty, default_problems[1])

# 创建全局题目生成服务实例
problem_generator_service = ProblemGeneratorService()