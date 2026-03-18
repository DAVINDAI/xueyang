from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Optional, Tuple
import re
import json
import threading
from app.services.llm import llm_service
from app.services.db import save_resume_optimization

class ResumeOptimizer:
    """
    简历优化服务，使用大模型分析和优化简历
    """
    
    def __init__(self, model_name: str = "qwen-plus"):
        """
        初始化简历优化器
        
        Args:
            model_name: 使用的大模型名称
        """
        self.model_name = model_name
    
    def _extract_job_title(self, job_description: str) -> str:
        """
        从职位描述中提取职位标题
        
        Args:
            job_description: 职位描述
            
        Returns:
            str: 职位标题
        """
        # 简单的提取逻辑：取第一行或包含职位关键字的行
        lines = job_description.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and len(line) < 100:
                # 检查是否包含职位相关关键字
                job_keywords = ['工程师', '开发', '程序员', '设计师', '产品', '运营', '经理', '主管', '专员']
                if any(keyword in line for keyword in job_keywords):
                    return line
        # 如果没有找到，返回默认标题
        return "未知职位"
    
    def optimize_resume(self, resume_content: str, job_description: str, visitor_id: str = None) -> Dict:
        """
        优化简历
        
        Args:
            resume_content: 原始简历内容
            job_description: 职位描述
            visitor_id: 访问者ID
            
        Returns:
            Dict: 包含优化结果的字典
        """
        # 生成优化后的简历
        optimized_resume_data = self._generate_optimized_resume(resume_content, job_description)
        
        # 生成面试准备建议
        interview_prep = self._generate_interview_preparation(
            optimized_resume_data.get('optimized_resume', resume_content),
            job_description
        )
        
        # 整合结果
        result = {
            "industry_analysis": optimized_resume_data.get('industry_analysis', ''),
            "optimized_resume": optimized_resume_data.get('optimized_resume', ''),
            "optimization_suggestions": optimized_resume_data.get('suggestions', []),
            "matching_analysis": optimized_resume_data.get('matching_analysis', {}),
            "interview_preparation": interview_prep
        }
        
        # 异步保存结果到数据库
        def save_to_db():
            try:
                job_title = self._extract_job_title(job_description)
                save_resume_optimization(
                    visitor_id=visitor_id,
                    job_title=job_title,
                    job_description=job_description,
                    industry_analysis=result.get('industry_analysis', ''),
                    optimized_resume=result.get('optimized_resume', ''),
                    optimization_suggestions=result.get('optimization_suggestions', []),
                    matching_analysis=result.get('matching_analysis', {}),
                    interview_preparation=result.get('interview_preparation', '')
                )
                print(f"简历优化结果已保存到数据库: {job_title}")
            except Exception as e:
                print(f"保存简历优化结果到数据库失败: {e}")
        
        # 启动线程保存，不阻塞主流程
        threading.Thread(target=save_to_db, daemon=True).start()
        
        return result
    
    def _generate_optimized_resume(self, resume_content: str, job_description: str) -> Dict:
        """
        使用大模型生成优化后的简历
        
        Args:
            resume_content: 原始简历内容
            job_description: 职位描述
            
        Returns:
            Dict: 包含优化结果的字典
        """
        # 定义提示词模板
        prompt_template = ChatPromptTemplate.from_template(
            """
            你是一位专业的简历优化专家，擅长根据不同行业的职位描述优化简历内容。
            
            首先，请分析以下职位描述所属的行业领域，然后根据该行业的特点和标准来优化简历。
            
            请根据以下职位描述和简历内容，完成以下任务：
            
            1. 分析职位描述的核心要求、关键词和所属行业
            2. 分析简历与职位要求的匹配度
            3. 识别简历中的优势和不足
            4. 生成符合目标行业标准的优化后简历内容
            5. 提供具体的优化建议，包括行业特定的改进点
            
            职位描述：
            {job_description}
            
            原简历内容：
            {resume_content}
            
            请按照以下JSON格式输出，确保格式正确可解析：
            
            {{
              "industryAnalysis": "分析职位所属的行业领域及其特点",
              "optimizedResume": "符合行业标准的优化后简历内容",
              "optimizationSuggestions": [
                "建议1",
                "建议2",
                "建议3"
              ],
              "matchingAnalysis": {{
                "coreSkills": "百分比",
                "workExperience": "百分比",
                "education": "百分比",
                "industryFit": "百分比"
              }}
            }}
            
            注意：
            - 只输出JSON，不要包含其他任何文本
            - 百分比格式示例：85%、90%等
            - 优化建议至少3条
            """
        )
        
        # 构建提示词
        prompt = prompt_template.format(
            job_description=job_description,
            resume_content=resume_content
        )
        
        # 调用大模型
        response = llm_service.generate_completion(self.model_name, prompt)
        
        # 解析响应
        return self._parse_optimization_response(response)
    
    def _generate_interview_preparation(self, optimized_resume: str, job_description: str) -> str:
        """
        生成面试准备建议
        
        Args:
            optimized_resume: 优化后的简历内容
            job_description: 职位描述
            
        Returns:
            str: 面试准备建议
        """
        # 定义提示词模板
        prompt_template = ChatPromptTemplate.from_template(
            """
            你是一位专业的面试辅导专家，擅长根据不同行业的职位要求和简历内容提供针对性的面试准备建议。
            
            首先，请分析以下职位描述所属的行业领域，然后根据该行业的面试特点和常见问题来提供准备建议。
            
            请根据以下职位描述和优化后的简历内容，完成以下任务：
            
            1. 分析职位的核心要求、可能的面试重点和所属行业
            2. 基于简历内容，识别可能被面试官关注的亮点和问题
            3. 生成针对该职位和行业的常见面试问题
            4. 提供每个问题的回答策略和建议，包括行业特定的回答技巧
            5. 提供技能准备和面试注意事项，包括行业文化和期望
            
            职位描述：
            {job_description}
            
            优化后的简历内容：
            {optimized_resume}
            
            请按照以下格式输出，确保内容全面且有针对性：
            
            ## 行业分析与面试重点
            [分析职位所属行业及其面试特点和重点]
            
            ## 常见面试问题
            1. [问题1]
            2. [问题2]
            3. [问题3]
            4. [问题4]
            5. [问题5]
            
            ## 回答策略
            ### 问题1
            [回答策略和建议，包括行业特定技巧]
            
            ### 问题2
            [回答策略和建议，包括行业特定技巧]
            
            ### 问题3
            [回答策略和建议，包括行业特定技巧]
            
            ### 问题4
            [回答策略和建议，包括行业特定技巧]
            
            ### 问题5
            [回答策略和建议，包括行业特定技巧]
            
            ## 技能准备建议
            [针对性的技能准备建议，包括行业特定技能]
            
            ## 面试注意事项
            [面试过程中的注意事项，包括行业文化和期望]
            """
        )
        
        # 构建提示词
        prompt = prompt_template.format(
            job_description=job_description,
            optimized_resume=optimized_resume
        )
        
        # 调用大模型
        response = llm_service.generate_completion(self.model_name, prompt)
        
        return response
    
    def _parse_optimization_response(self, response: str) -> Dict:
        """
        解析优化响应内容（JSON格式）
        
        Args:
            response: 大模型的响应内容
            
        Returns:
            Dict: 解析后的结果
        """
        result = {
            "industry_analysis": "",
            "optimized_resume": "",
            "suggestions": [],
            "matching_analysis": {}
        }
        
        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'(\{[\s\S]*\})', response)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # 映射字段
                if data.get("industryAnalysis"):
                    result["industry_analysis"] = data["industryAnalysis"]
                
                if data.get("optimizedResume"):
                    result["optimized_resume"] = data["optimizedResume"]
                
                if data.get("optimizationSuggestions"):
                    result["suggestions"] = data["optimizationSuggestions"]
                
                if data.get("matchingAnalysis"):
                    result["matching_analysis"] = data["matchingAnalysis"]
            else:
                print("警告：未能从响应中提取JSON")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"响应内容: {response[:200]}...")
        except Exception as e:
            print(f"解析响应时发生错误: {e}")
        
        return result

# 创建全局简历优化服务实例
resume_optimizer_service = ResumeOptimizer()