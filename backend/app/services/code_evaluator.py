from typing import Dict, Any
import logging
from app.services.llm import llm_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeEvaluatorService:
    def __init__(self):
        self.model_name = "glm-5"  # 使用GLM大模型
        self.max_debug_attempts = 5  # 最多调试5次
    
    def evaluate_code(self, problem: Dict[str, Any], user_code: str) -> Dict[str, Any]:
        """评估用户代码"""
        try:
            # 构建提示词
            prompt = self._build_evaluation_prompt(problem, user_code)
            
            # 调用大模型进行评估
            response = llm_service.generate_completion(self.model_name, prompt)
            
            # 解析评估结果
            evaluation = self._parse_evaluation(response)
            
            # 调试代码（最多5次）
            if not evaluation.get("is_correct", False):
                logger.info(f"代码评估错误，开始调试...")

            # 这里不仅仅是调用大模型，要本地运行代码，评估是否正确 
            # 将本地运行代码的结果作为提示词信息，引导大模型生成修复代码
            # 创建LangGraph节点, 用LangGraph图的方式实现react循环调试
            debug_attempts = 0
            while not evaluation.get("is_correct", False) and debug_attempts < self.max_debug_attempts:
                debug_prompt = self._build_debug_prompt(problem, user_code, evaluation.get("errors", []))
                debug_response = llm_service.generate_completion(self.model_name, debug_prompt)
                debug_result = self._parse_debug_result(debug_response)
                
                if debug_result.get("fixed_code"):
                    user_code = debug_result["fixed_code"]
                    # 重新评估
                    re_eval_prompt = self._build_evaluation_prompt(problem, user_code)
                    re_eval_response = llm_service.generate_completion(self.model_name, re_eval_prompt)
                    evaluation = self._parse_evaluation(re_eval_response)
                
                debug_attempts += 1
            
            evaluation["debug_attempts"] = debug_attempts
            evaluation["final_code"] = user_code
            
            return evaluation
        except Exception as e:
            logger.error(f"评估代码失败: {e}")
            return {
                "is_correct": False,
                "errors": [str(e)],
                "suggestions": ["代码评估过程中发生错误"],
                "debug_attempts": 0,
                "final_code": user_code
            }
    
    def _build_evaluation_prompt(self, problem: Dict[str, Any], user_code: str) -> str:
        """构建评估提示词"""
        prompt = f"请评估以下代码是否正确解决了给定的算法问题：\n"
        prompt += f"\n题目：{problem['title']}\n"
        prompt += f"\n描述：{problem['description']}\n"
        prompt += "\n示例：\n"
        for i, example in enumerate(problem['examples']):
            prompt += f"示例 {i+1}:\n"
            prompt += f"输入: {example['input']}\n"
            prompt += f"输出: {example['output']}\n"
        prompt += f"\n用户代码：\n{user_code}\n"
        prompt += "\n请分析代码是否正确，指出存在的问题，并提供改进建议。\n"
        prompt += "请按照以下JSON格式输出评估结果：\n"
        prompt += "{\n"
        prompt += "  \"is_correct\": true/false,\n"
        prompt += "  \"errors\": [\"错误1\", \"错误2\"],\n"
        prompt += "  \"suggestions\": [\"建议1\", \"建议2\"],\n"
        prompt += "  \"quality_score\": 0-100,\n"
        prompt += "  \"explanation\": \"详细解释\"\n"
        prompt += "}\n"
        
        return prompt
    
    def _build_debug_prompt(self, problem: Dict[str, Any], user_code: str, errors: list) -> str:
        """构建调试提示词"""
        prompt = f"请调试以下代码，使其正确解决给定的算法问题：\n"
        prompt += f"\n题目：{problem['title']}\n"
        prompt += f"\n描述：{problem['description']}\n"
        prompt += "\n示例：\n"
        for i, example in enumerate(problem['examples']):
            prompt += f"示例 {i+1}:\n"
            prompt += f"输入: {example['input']}\n"
            prompt += f"输出: {example['output']}\n"
        prompt += f"\n用户代码：\n{user_code}\n"
        prompt += "\n存在的问题：\n"
        for error in errors:
            prompt += f"- {error}\n"
        prompt += "\n请修复代码，并提供修复后的完整代码。\n"
        prompt += "请按照以下JSON格式输出修复结果：\n"
        prompt += "{\n"
        prompt += "  \"fixed_code\": \"修复后的代码\",\n"
        prompt += "  \"fix_explanation\": \"修复解释\"\n"
        prompt += "}\n"
        
        return prompt
    
    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """解析评估结果"""
        import json
        
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"解析评估结果失败: {e}")
        
        # 解析失败，返回默认结果
        return {
            "is_correct": False,
            "errors": ["无法解析评估结果"],
            "suggestions": [],
            "quality_score": 0,
            "explanation": "评估结果解析失败"
        }
    
    def _parse_debug_result(self, response: str) -> Dict[str, Any]:
        """解析调试结果"""
        import json
        
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"解析调试结果失败: {e}")
        
        # 解析失败，返回默认结果
        return {
            "fixed_code": None,
            "fix_explanation": "调试结果解析失败"
        }

# 创建全局代码评估服务实例
code_evaluator_service = CodeEvaluatorService()