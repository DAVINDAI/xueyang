from typing import Dict, Any, List, Optional
import logging
import subprocess
import sys
import io
import contextlib
import time
import ast
from app.services.llm import llm_service
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义状态类型
class CodeState(BaseModel):
    problem: Dict[str, Any]
    user_code: str
    errors: List[str] = Field(default_factory=list)
    debug_attempts: int = 0
    final_code: Optional[str] = None
    is_correct: bool = False
    quality_score: int = 0
    explanation: str = ""
    suggestions: List[str] = Field(default_factory=list)
    execution_results: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)

class CodeEvaluatorServicePro:
    def __init__(self):
        self.model_name = "glm-5"  # 使用GLM大模型
        self.max_debug_attempts = 5  # 最多调试5次
        self.timeout_seconds = 10  # 代码执行超时时间
    
    def evaluate_code(self, problem: Dict[str, Any], user_code: str) -> Dict[str, Any]:
        """评估用户代码（Pro版本）"""
        logger.info(f"========== 开始评估代码 ==========")
        logger.info(f"题目: {problem.get('title', 'Unknown')}")
        logger.info(f"代码长度: {len(user_code)} 字符")
        
        try:
            # 1. 代码静态分析
            logger.info("[步骤 1/7] 开始代码静态分析...")
            static_analysis = self._static_code_analysis(user_code)
            logger.info(f"[步骤 1/7] 静态分析完成 - 语法错误: {static_analysis.get('syntax_error')}, 复杂度: {static_analysis.get('complexity')}, 潜在问题: {len(static_analysis.get('potential_issues', []))}")
            
            # 2. 本地运行代码，评估是否正确
            logger.info("[步骤 2/7] 开始本地运行代码...")
            execution_results = self._run_code_locally(problem, user_code)
            logger.info(f"[步骤 2/7] 本地运行完成 - 成功: {execution_results.get('success')}, 错误数: {len(execution_results.get('errors', []))}")
            
            # 3. 性能分析
            logger.info("[步骤 3/7] 开始性能分析...")
            performance_metrics = self._analyze_performance(problem, user_code)
            logger.info(f"[步骤 3/7] 性能分析完成 - 平均执行时间: {performance_metrics.get('average_execution_time', 0):.4f}秒, 时间复杂度: {performance_metrics.get('time_complexity')}")
            
            # 4. 构建提示词，包含本地运行结果和静态分析
            logger.info("[步骤 4/7] 构建评估提示词...")
            prompt = self._build_evaluation_prompt(problem, user_code, execution_results, static_analysis, performance_metrics)
            logger.info(f"[步骤 4/7] 提示词构建完成 - 长度: {len(prompt)} 字符")
            
            # 5. 调用大模型进行评估
            logger.info(f"[步骤 5/7] 调用大模型进行评估 - 模型: {self.model_name}...")
            response = llm_service.generate_completion(self.model_name, prompt)
            logger.info(f"[步骤 5/7] 大模型评估完成 - 响应长度: {len(response)} 字符")
            
            # 6. 解析评估结果
            logger.info("[步骤 6/7] 解析评估结果...")
            evaluation = self._parse_evaluation(response)
            logger.info(f"[步骤 6/7] 评估结果解析完成 - 是否正确: {evaluation.get('is_correct')}, 质量评分: {evaluation.get('quality_score')}")
            
            # 7. 使用LangGraph实现智能循环调试
            if not evaluation.get("is_correct", False):
                logger.info(f"[步骤 7/7] 代码评估错误，开始使用LangGraph智能调试...")
                debug_result = self._debug_with_langgraph(problem, user_code, evaluation.get("errors", []))
                evaluation.update(debug_result)
                logger.info(f"[步骤 7/7] LangGraph调试完成 - 调试次数: {evaluation.get('debug_attempts')}, 最终是否正确: {evaluation.get('is_correct')}")
            else:
                logger.info("[步骤 7/7] 代码评估正确，无需调试")
                evaluation["debug_attempts"] = 0
                evaluation["final_code"] = user_code
                evaluation["performance_metrics"] = performance_metrics
            
            logger.info(f"========== 代码评估完成 ==========")
            return evaluation
        except Exception as e:
            logger.error(f"评估代码失败: {e}")
            return {
                "is_correct": False,
                "errors": [str(e)],
                "suggestions": ["代码评估过程中发生错误"],
                "debug_attempts": 0,
                "final_code": user_code,
                "performance_metrics": {}
            }
    
    def _static_code_analysis(self, code: str) -> Dict[str, Any]:
        """代码静态分析"""
        analysis = {
            "syntax_error": False,
            "complexity": 0,
            "potential_issues": [],
            "code_structure": {}
        }
        
        try:
            # 解析代码
            tree = ast.parse(code)
            
            # 计算代码复杂度
            analysis["complexity"] = self._calculate_complexity(tree)
            
            # 检查潜在问题
            analysis["potential_issues"] = self._detect_potential_issues(tree)
            
            # 分析代码结构
            analysis["code_structure"] = self._analyze_code_structure(tree)
            
        except SyntaxError as e:
            analysis["syntax_error"] = True
            analysis["potential_issues"].append(f"语法错误: {e.msg}")
        except Exception as e:
            analysis["potential_issues"].append(f"静态分析失败: {str(e)}")
        
        return analysis
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """计算代码复杂度"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1
            
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
            
            def visit_Break(self, node):
                self.complexity += 0.5
                self.generic_visit(node)
            
            def visit_Continue(self, node):
                self.complexity += 0.5
                self.generic_visit(node)
            
            def visit_Raise(self, node):
                self.complexity += 0.5
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return int(visitor.complexity)
    
    def _detect_potential_issues(self, tree: ast.AST) -> List[str]:
        """检测潜在问题"""
        issues = []
        
        class IssueVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
            
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name in ["os", "subprocess", "eval", "exec"]:
                        self.issues.append(f"使用了潜在的危险模块: {alias.name}")
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec", "compile"]:
                    self.issues.append("使用了潜在的危险函数: eval/exec/compile")
                self.generic_visit(node)
        
        visitor = IssueVisitor()
        visitor.visit(tree)
        return visitor.issues
    
    def _analyze_code_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """分析代码结构"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        class StructureVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.classes = []
                self.imports = []
            
            def visit_FunctionDef(self, node):
                self.functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno
                })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                self.classes.append({
                    "name": node.name,
                    "line": node.lineno
                })
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append(alias.name)
            
            def visit_ImportFrom(self, node):
                for alias in node.names:
                    self.imports.append(f"{node.module}.{alias.name}")
        
        visitor = StructureVisitor()
        visitor.visit(tree)
        structure["functions"] = visitor.functions
        structure["classes"] = visitor.classes
        structure["imports"] = visitor.imports
        
        return structure
    
    def _run_code_locally(self, problem: Dict[str, Any], user_code: str) -> Dict[str, Any]:
        """本地运行代码"""
        results = {
            "success": False,
            "outputs": [],
            "errors": [],
            "execution_times": []
        }
        
        # 提取示例输入
        examples = problem.get("examples", [])
        
        for example in examples:
            try:
                # 构建测试代码
                test_code = self._build_test_code(user_code, example["input"])
                
                # 运行代码并计时
                start_time = time.time()
                output, error = self._execute_code(test_code)
                execution_time = time.time() - start_time
                
                results["execution_times"].append(execution_time)
                
                if error:
                    results["errors"].append(f"示例输入 {example['input']} 运行错误: {error}")
                else:
                    results["outputs"].append({
                        "input": example["input"],
                        "expected": example["output"],
                        "actual": output.strip(),
                        "execution_time": execution_time
                    })
            except Exception as e:
                results["errors"].append(f"运行示例 {example['input']} 时发生异常: {str(e)}")
        
        # 检查是否所有示例都通过
        if not results["errors"]:
            all_correct = True
            for output in results["outputs"]:
                if output["actual"] != output["expected"]:
                    all_correct = False
                    results["errors"].append(f"示例输入 {output['input']} 输出不匹配: 期望 {output['expected']}, 实际 {output['actual']}")
            results["success"] = all_correct
        
        return results
    
    def _build_test_code(self, user_code: str, input_data: str) -> str:
        """构建测试代码"""
        # 假设用户代码实现了一个函数，我们需要调用它
        test_code = f"""
{user_code}

# 测试代码
if __name__ == "__main__":
    # 解析输入
    input_data = {input_data}
    # 调用函数
    result = find_index(input_data[0], input_data[1])
    print(result)
"""
        return test_code
    
    def _execute_code(self, code: str) -> tuple:
        """执行代码并返回输出和错误"""
        try:
            # 创建一个新的进程来执行代码
            process = subprocess.Popen(
                [sys.executable, "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout_seconds
            )
            stdout, stderr = process.communicate()
            return stdout, stderr
        except subprocess.TimeoutExpired:
            return "", "代码执行超时"
        except Exception as e:
            return "", str(e)
    
    def _analyze_performance(self, problem: Dict[str, Any], user_code: str) -> Dict[str, Any]:
        """性能分析"""
        metrics = {
            "average_execution_time": 0,
            "memory_usage": 0,
            "time_complexity": "Unknown",
            "space_complexity": "Unknown"
        }
        
        # 运行多次取平均值
        execution_times = []
        examples = problem.get("examples", [])
        
        for example in examples:
            try:
                test_code = self._build_test_code(user_code, example["input"])
                start_time = time.time()
                self._execute_code(test_code)
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            except Exception:
                pass
        
        if execution_times:
            metrics["average_execution_time"] = sum(execution_times) / len(execution_times)
        
        # 简单的时间复杂度分析
        if "for" in user_code and "for" in user_code[user_code.find("for") + 1:]:
            metrics["time_complexity"] = "O(n²)"
        elif "for" in user_code or "while" in user_code:
            metrics["time_complexity"] = "O(n)"
        else:
            metrics["time_complexity"] = "O(1)"
        
        return metrics
    
    def _build_evaluation_prompt(self, problem: Dict[str, Any], user_code: str, 
                                execution_results: Dict[str, Any], 
                                static_analysis: Dict[str, Any],
                                performance_metrics: Dict[str, Any]) -> str:
        """构建评估提示词，包含本地运行结果、静态分析和性能分析"""
        prompt = f"请评估以下代码是否正确解决了给定的算法问题：\n"
        prompt += f"\n题目：{problem['title']}\n"
        prompt += f"\n描述：{problem['description']}\n"
        prompt += "\n示例：\n"
        for i, example in enumerate(problem['examples']):
            prompt += f"示例 {i+1}:\n"
            prompt += f"输入: {example['input']}\n"
            prompt += f"输出: {example['output']}\n"
        prompt += f"\n用户代码：\n{user_code}\n"
        
        # 添加本地运行结果
        prompt += "\n本地运行结果：\n"
        if execution_results.get("success"):
            prompt += "✓ 所有示例运行正确\n"
            if execution_results.get("execution_times"):
                avg_time = sum(execution_results["execution_times"]) / len(execution_results["execution_times"])
                prompt += f"平均执行时间: {avg_time:.4f}秒\n"
        else:
            prompt += "✗ 运行存在问题：\n"
            for error in execution_results.get("errors", []):
                prompt += f"- {error}\n"
        
        # 添加静态分析结果
        prompt += "\n静态分析结果：\n"
        if static_analysis.get("syntax_error"):
            prompt += "✗ 存在语法错误\n"
        else:
            prompt += f"✓ 语法正确\n"
            prompt += f"代码复杂度: {static_analysis.get('complexity', 0)}\n"
            if static_analysis.get("potential_issues"):
                prompt += "潜在问题：\n"
                for issue in static_analysis["potential_issues"]:
                    prompt += f"- {issue}\n"
        
        # 添加性能分析结果
        prompt += "\n性能分析结果：\n"
        prompt += f"平均执行时间: {performance_metrics.get('average_execution_time', 0):.4f}秒\n"
        prompt += f"时间复杂度: {performance_metrics.get('time_complexity', 'Unknown')}\n"
        prompt += f"空间复杂度: {performance_metrics.get('space_complexity', 'Unknown')}\n"
        
        prompt += "\n请分析代码是否正确，指出存在的问题，并提供改进建议。\n"
        prompt += "请按照以下JSON格式输出评估结果：\n"
        prompt += "{\n"
        prompt += "  \"is_correct\": true/false,\n"
        prompt += "  \"errors\": [\"错误1\", \"错误2\"],\n"
        prompt += "  \"suggestions\": [\"建议1\", \"建议2\"],\n"
        prompt += "  \"quality_score\": 0-100,\n"
        prompt += "  \"explanation\": \"详细解释\",\n"
        prompt += "  \"performance_feedback\": \"性能反馈\",\n"
        prompt += "  \"code_style_feedback\": \"代码风格反馈\"\n"
        prompt += "}\n"
        
        return prompt
    
    def _debug_with_langgraph(self, problem: Dict[str, Any], user_code: str, initial_errors: List[str]) -> Dict[str, Any]:
        """使用LangGraph实现智能循环调试"""
        logger.info(f"  [LangGraph] 开始创建调试工作流...")
        logger.info(f"  [LangGraph] 初始错误数: {len(initial_errors)}")
        
        # 定义状态
        initial_state = CodeState(
            problem=problem,
            user_code=user_code,
            errors=initial_errors,
            debug_attempts=0,
            final_code=user_code
        )
        logger.info(f"  [LangGraph] 初始状态创建完成")
        
        # 创建LangGraph
        graph = StateGraph(CodeState)
        
        # 添加节点
        graph.add_node("generate_fix", self._generate_fix_node)
        graph.add_node("test_fix", self._test_fix_node)
        graph.add_node("evaluate_fix", self._evaluate_fix_node)
        graph.add_node("optimize_code", self._optimize_code_node)
        
        # 添加边
        graph.set_entry_point("generate_fix")
        graph.add_edge("generate_fix", "test_fix")
        graph.add_conditional_edges(
            "test_fix",
            self._should_continue_debugging,
            {
                "continue": "evaluate_fix",
                "stop": "optimize_code"
            }
        )
        def should_continue_from_evaluate(state):
            if isinstance(state, dict):
                is_correct = state.get("is_correct", False)
                debug_attempts = state.get("debug_attempts", 0)
            else:
                is_correct = state.is_correct
                debug_attempts = state.debug_attempts
            return "continue" if not is_correct and debug_attempts < self.max_debug_attempts else "stop"
        
        graph.add_conditional_edges(
            "evaluate_fix",
            should_continue_from_evaluate,
            {
                "continue": "generate_fix",
                "stop": "optimize_code"
            }
        )
        graph.add_edge("optimize_code", END)
        
        # 编译并运行图
        logger.info(f"  [LangGraph] 编译工作流...")
        app = graph.compile()
        logger.info(f"  [LangGraph] 开始执行调试工作流...")
        result = app.invoke(initial_state)
        logger.info(f"  [LangGraph] 调试工作流执行完成")
        
        # LangGraph返回的是字典，需要正确处理
        if isinstance(result, dict):
            debug_attempts = result.get("debug_attempts", 0)
            is_correct = result.get("is_correct", False)
            logger.info(f"  [LangGraph] 调试结果 - 尝试次数: {debug_attempts}, 最终正确: {is_correct}")
            return {
                "is_correct": is_correct,
                "errors": result.get("errors", []),
                "suggestions": result.get("suggestions", []),
                "quality_score": result.get("quality_score", 0),
                "explanation": result.get("explanation", ""),
                "debug_attempts": debug_attempts,
                "final_code": result.get("final_code", user_code),
                "performance_metrics": result.get("performance_metrics", {})
            }
        else:
            # 构建返回结果（CodeState对象）
            logger.info(f"  [LangGraph] 调试结果 - 尝试次数: {result.debug_attempts}, 最终正确: {result.is_correct}")
            return {
                "is_correct": result.is_correct,
                "errors": result.errors,
                "suggestions": result.suggestions,
                "quality_score": result.quality_score,
                "explanation": result.explanation,
                "debug_attempts": result.debug_attempts,
                "final_code": result.final_code,
                "performance_metrics": result.performance_metrics
            }
    
    def _generate_fix_node(self, state):
        """生成修复代码的节点"""
        logger.info(f"    [节点: generate_fix] 开始生成修复代码...")
        
        if isinstance(state, dict):
            problem = state.get("problem", {})
            user_code = state.get("user_code", "")
            errors = state.get("errors", [])
            debug_attempts = state.get("debug_attempts", 0)
        else:
            problem = state.problem
            user_code = state.user_code
            errors = state.errors
            debug_attempts = state.debug_attempts
        
        logger.info(f"    [节点: generate_fix] 当前调试次数: {debug_attempts}, 错误数: {len(errors)}")
        
        # 构建调试提示词
        prompt = f"请调试以下代码，使其正确解决给定的算法问题：\n"
        prompt += f"\n题目：{problem.get('title', '')}\n"
        prompt += f"\n描述：{problem.get('description', '')}\n"
        prompt += "\n示例：\n"
        for i, example in enumerate(problem.get('examples', [])):
            prompt += f"示例 {i+1}:\n"
            prompt += f"输入: {example['input']}\n"
            prompt += f"输出: {example['output']}\n"
        prompt += f"\n用户代码：\n{user_code}\n"
        prompt += "\n存在的问题：\n"
        for error in errors:
            prompt += f"- {error}\n"
        prompt += "\n请修复代码，并提供修复后的完整代码。\n"
        prompt += "修复时请考虑以下因素：\n"
        prompt += "1. 代码正确性\n"
        prompt += "2. 代码性能\n"
        prompt += "3. 代码可读性\n"
        prompt += "4. 代码风格\n"
        prompt += "请按照以下JSON格式输出修复结果：\n"
        prompt += "{\n"
        prompt += "  \"fixed_code\": \"修复后的代码\",\n"
        prompt += "  \"fix_explanation\": \"修复解释\",\n"
        prompt += "  \"optimization_suggestions\": [\"优化建议1\", \"优化建议2\"]\n"
        prompt += "}\n"
        
        # 调用大模型生成修复
        logger.info(f"    [节点: generate_fix] 调用大模型生成修复...")
        response = llm_service.generate_completion(self.model_name, prompt)
        debug_result = self._parse_debug_result(response)
        
        if debug_result.get("fixed_code"):
            logger.info(f"    [节点: generate_fix] 成功生成修复代码")
            if isinstance(state, dict):
                state["user_code"] = debug_result["fixed_code"]
            else:
                state.user_code = debug_result["fixed_code"]
        else:
            logger.warning(f"    [节点: generate_fix] 未能生成修复代码")
        
        if isinstance(state, dict):
            state["debug_attempts"] = debug_attempts + 1
        else:
            state.debug_attempts = debug_attempts + 1
        
        logger.info(f"    [节点: generate_fix] 完成，调试次数更新为: {debug_attempts + 1}")
        return state
    
    def _test_fix_node(self, state):
        """测试修复代码的节点"""
        logger.info(f"    [节点: test_fix] 开始测试修复后的代码...")
        
        if isinstance(state, dict):
            problem = state.get("problem", {})
            user_code = state.get("user_code", "")
        else:
            problem = state.problem
            user_code = state.user_code
        
        # 本地运行修复后的代码
        logger.info(f"    [节点: test_fix] 本地运行代码...")
        execution_results = self._run_code_locally(problem, user_code)
        
        # 性能分析
        logger.info(f"    [节点: test_fix] 性能分析...")
        performance_metrics = self._analyze_performance(problem, user_code)
        
        success = execution_results.get("success", False)
        logger.info(f"    [节点: test_fix] 运行结果 - 成功: {success}, 错误数: {len(execution_results.get('errors', []))}")
        
        if isinstance(state, dict):
            state["execution_results"] = execution_results
            state["performance_metrics"] = performance_metrics
            if success:
                state["is_correct"] = True
                state["errors"] = []
                logger.info(f"    [节点: test_fix] 代码测试通过 ✓")
            else:
                state["errors"] = execution_results.get("errors", [])
                logger.info(f"    [节点: test_fix] 代码测试失败 ✗")
        else:
            state.execution_results = execution_results
            state.performance_metrics = performance_metrics
            if success:
                state.is_correct = True
                state.errors = []
                logger.info(f"    [节点: test_fix] 代码测试通过 ✓")
            else:
                state.errors = execution_results.get("errors", [])
                logger.info(f"    [节点: test_fix] 代码测试失败 ✗")
        
        return state
    
    def _evaluate_fix_node(self, state):
        """评估修复结果的节点"""
        logger.info(f"    [节点: evaluate_fix] 开始评估修复结果...")
        
        if isinstance(state, dict):
            problem = state.get("problem", {})
            user_code = state.get("user_code", "")
            execution_results = state.get("execution_results", {})
            performance_metrics = state.get("performance_metrics", {})
        else:
            problem = state.problem
            user_code = state.user_code
            execution_results = state.execution_results
            performance_metrics = state.performance_metrics
        
        # 静态分析
        logger.info(f"    [节点: evaluate_fix] 执行静态分析...")
        static_analysis = self._static_code_analysis(user_code)
        
        # 构建评估提示词
        logger.info(f"    [节点: evaluate_fix] 构建评估提示词...")
        prompt = self._build_evaluation_prompt(
            problem, 
            user_code, 
            execution_results, 
            static_analysis,
            performance_metrics
        )
        
        # 调用大模型进行评估
        logger.info(f"    [节点: evaluate_fix] 调用大模型评估...")
        response = llm_service.generate_completion(self.model_name, prompt)
        evaluation = self._parse_evaluation(response)
        
        is_correct = evaluation.get("is_correct", False)
        quality_score = evaluation.get("quality_score", 0)
        logger.info(f"    [节点: evaluate_fix] 评估完成 - 是否正确: {is_correct}, 质量评分: {quality_score}")
        
        if isinstance(state, dict):
            state["is_correct"] = is_correct
            state["errors"] = evaluation.get("errors", [])
            state["suggestions"] = evaluation.get("suggestions", [])
            state["quality_score"] = quality_score
            state["explanation"] = evaluation.get("explanation", "")
            state["final_code"] = user_code
        else:
            state.is_correct = is_correct
            state.errors = evaluation.get("errors", [])
            state.suggestions = evaluation.get("suggestions", [])
            state.quality_score = quality_score
            state.explanation = evaluation.get("explanation", "")
            state.final_code = user_code
        
        return state
    
    def _optimize_code_node(self, state):
        """优化代码的节点"""
        logger.info(f"    [节点: optimize_code] 开始优化代码...")
        
        if isinstance(state, dict):
            is_correct = state.get("is_correct", False)
            problem = state.get("problem", {})
            user_code = state.get("user_code", "")
            performance_metrics = state.get("performance_metrics", {})
        else:
            is_correct = state.is_correct
            problem = state.problem
            user_code = state.user_code
            performance_metrics = state.performance_metrics
        
        if is_correct:
            logger.info(f"    [节点: optimize_code] 代码正确，开始性能优化...")
            # 构建优化提示词
            prompt = f"请优化以下代码，提高其性能和可读性：\n"
            prompt += f"\n题目：{problem.get('title', '')}\n"
            prompt += f"\n用户代码：\n{user_code}\n"
            prompt += "\n当前性能：\n"
            prompt += f"平均执行时间: {performance_metrics.get('average_execution_time', 0):.4f}秒\n"
            prompt += f"时间复杂度: {performance_metrics.get('time_complexity', 'Unknown')}\n"
            prompt += "\n请提供优化后的代码，并解释优化的原因。\n"
            prompt += "请按照以下JSON格式输出优化结果：\n"
            prompt += "{\n"
            prompt += "  \"optimized_code\": \"优化后的代码\",\n"
            prompt += "  \"optimization_explanation\": \"优化解释\"\n"
            prompt += "}\n"
            
            # 调用大模型进行优化
            logger.info(f"    [节点: optimize_code] 调用大模型进行优化...")
            response = llm_service.generate_completion(self.model_name, prompt)
            optimization_result = self._parse_optimization_result(response)
            
            if optimization_result.get("optimized_code"):
                logger.info(f"    [节点: optimize_code] 成功生成优化代码")
                if isinstance(state, dict):
                    state["final_code"] = optimization_result["optimized_code"]
                else:
                    state.final_code = optimization_result["optimized_code"]
            else:
                logger.info(f"    [节点: optimize_code] 未能生成优化代码，使用原代码")
                if isinstance(state, dict):
                    state["final_code"] = user_code
                else:
                    state.final_code = user_code
        else:
            logger.info(f"    [节点: optimize_code] 代码不正确，跳过优化")
            if isinstance(state, dict):
                state["final_code"] = user_code
            else:
                state.final_code = user_code
        
        return state
    
    def _should_continue_debugging(self, state) -> str:
        """决定是否继续调试"""
        if isinstance(state, dict):
            is_correct = state.get("is_correct", False)
            debug_attempts = state.get("debug_attempts", 0)
        else:
            is_correct = state.is_correct
            debug_attempts = state.debug_attempts
        
        if is_correct:
            logger.info(f"    [条件判断] 代码已正确，停止调试")
            return "stop"
        elif debug_attempts >= self.max_debug_attempts:
            logger.info(f"    [条件判断] 达到最大调试次数({self.max_debug_attempts})，停止调试")
            return "stop"
        else:
            logger.info(f"    [条件判断] 继续调试，当前次数: {debug_attempts}")
            return "continue"
    
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
            "explanation": "评估结果解析失败",
            "performance_feedback": "",
            "code_style_feedback": ""
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
            "fix_explanation": "调试结果解析失败",
            "optimization_suggestions": []
        }
    
    def _parse_optimization_result(self, response: str) -> Dict[str, Any]:
        """解析优化结果"""
        import json
        
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"解析优化结果失败: {e}")
        
        # 解析失败，返回默认结果
        return {
            "optimized_code": None,
            "optimization_explanation": "优化结果解析失败"
        }

# 创建全局代码评估服务实例
code_evaluator_service_pro = CodeEvaluatorServicePro()
