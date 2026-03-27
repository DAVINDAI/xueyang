import os
import json
import logging
from datetime import datetime, timedelta
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langsmith import Client
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 提示词管理服务
class PromptManagerService:
    def __init__(self):
        # 初始化 LangSmith 客户端
        self.client = Client()
        # 本地缓存
        self.prompt_cache = {}
        # 缓存过期时间（秒）
        self.cache_expiry = 3600  # 1小时
        # 缓存文件路径
        self.cache_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "prompt_cache.json"
        )
        # 确保缓存目录存在
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        # 加载本地缓存
        self._load_cache()
    
    def _load_cache(self):
        """加载本地缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # 检查缓存是否过期
                    current_time = datetime.now().timestamp()
                    for key, value in cached_data.items():
                        if current_time - value.get('timestamp', 0) < self.cache_expiry:
                            self.prompt_cache[key] = value
                        else:
                            logger.info(f"缓存过期: {key}")
        except Exception as e:
            logger.error(f"加载缓存失败: {str(e)}")
    
    def _save_cache(self):
        """保存本地缓存"""
        try:
            # 更新缓存时间戳
            for key in self.prompt_cache:
                self.prompt_cache[key]['timestamp'] = datetime.now().timestamp()
            # 保存到文件
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompt_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
    
    def get_prompt(self, prompt_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        从 LangSmith 获取提示词
        
        参数:
            prompt_name: 提示词名称
            default: 默认提示词，如果 LangSmith 中不存在则使用
            
        返回:
            str: 提示词内容
        """
        try:
            # 检查缓存
            if prompt_name in self.prompt_cache:
                cached_prompt = self.prompt_cache[prompt_name]
                # 检查缓存是否过期
                if datetime.now().timestamp() - cached_prompt.get('timestamp', 0) < self.cache_expiry:
                    logger.info(f"从缓存获取提示词: {prompt_name}")
                    return cached_prompt['content']
            
            # 从 LangSmith 获取
            logger.info(f"从 LangSmith 获取提示词: {prompt_name}")
            
            # 尝试获取提示词
            try:
                prompts = self.client.list_prompts()
                for prompt in prompts:
                    if prompt.name == prompt_name:
                        # 获取提示词版本
                        versions = self.client.list_prompt_versions(prompt.id)
                        if versions:
                            # 使用最新版本
                            latest_version = versions[0]
                            content = latest_version.prompt.content
                            # 更新缓存
                            self.prompt_cache[prompt_name] = {
                                'content': content,
                                'timestamp': datetime.now().timestamp()
                            }
                            self._save_cache()
                            return content
            except Exception as e:
                logger.warning(f"从 LangSmith 获取提示词失败: {str(e)}")
                # 如果失败，使用默认值
                if default:
                    logger.info(f"使用默认提示词: {prompt_name}")
                    # 更新缓存
                    self.prompt_cache[prompt_name] = {
                        'content': default,
                        'timestamp': datetime.now().timestamp()
                    }
                    self._save_cache()
                    return default
            
            return default
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return default
    
    def get_chat_prompt(self, system_prompt_name: str, human_prompt: str, default_system_prompt: Optional[str] = None) -> ChatPromptTemplate:
        """
        获取聊天提示词模板
        
        参数:
            system_prompt_name: 系统提示词名称
            human_prompt: 人类提示词模板
            default_system_prompt: 默认系统提示词
            
        返回:
            ChatPromptTemplate: 聊天提示词模板
        """
        # 获取系统提示词
        system_prompt = self.get_prompt(system_prompt_name, default_system_prompt)
        
        # 创建聊天提示词模板
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_prompt)
        ])
        
        return chat_prompt
    
    def clear_cache(self):
        """清除缓存"""
        self.prompt_cache.clear()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        logger.info("缓存已清除")
    
    def refresh_prompt(self, prompt_name: str) -> Optional[str]:
        """
        刷新提示词
        
        参数:
            prompt_name: 提示词名称
            
        返回:
            str: 最新的提示词内容
        """
        # 从缓存中删除
        if prompt_name in self.prompt_cache:
            del self.prompt_cache[prompt_name]
        # 重新获取
        return self.get_prompt(prompt_name)
    
    def upload_prompt(self, prompt_name: str, prompt_content: str, description: Optional[str] = None) -> bool:
        """
        上传提示词到 LangSmith
        
        参数:
            prompt_name: 提示词名称
            prompt_content: 提示词内容
            description: 提示词描述
            
        返回:
            bool: 是否上传成功
        """
        try:
            logger.info(f"上传提示词到 LangSmith: {prompt_name}")
            
            # 创建 PromptTemplate 对象
            prompt_template = PromptTemplate.from_template(prompt_content)
            
            # 使用 push_prompt 上传提示词
            # 尝试使用简单的名称格式
            self.client.push_prompt(
                prompt_identifier=prompt_name,
                object=prompt_template,
                description=description or f"提示词: {prompt_name}",
                is_public=False
            )
            
            # 更新缓存
            self.prompt_cache[prompt_name] = {
                'content': prompt_content,
                'timestamp': datetime.now().timestamp()
            }
            self._save_cache()
            
            logger.info(f"提示词 '{prompt_name}' 上传成功")
            return True
            
        except Exception as e:
            logger.error(f"上传提示词失败: {str(e)}")
            return False
    
    def update_prompt(self, prompt_name: str, prompt_content: str, description: Optional[str] = None) -> bool:
        """
        更新 LangSmith 中的提示词
        
        参数:
            prompt_name: 提示词名称
            prompt_content: 新的提示词内容
            description: 提示词描述
            
        返回:
            bool: 是否更新成功
        """
        try:
            logger.info(f"更新 LangSmith 中的提示词: {prompt_name}")
            
            # 创建 PromptTemplate 对象
            prompt_template = PromptTemplate.from_template(prompt_content)
            
            # 使用 push_prompt 更新提示词（如果不存在会自动创建）
            self.client.push_prompt(
                prompt_identifier=prompt_name,
                object=prompt_template,
                description=description or f"提示词: {prompt_name}"
            )
            
            # 更新缓存
            self.prompt_cache[prompt_name] = {
                'content': prompt_content,
                'timestamp': datetime.now().timestamp()
            }
            self._save_cache()
            
            logger.info(f"提示词 '{prompt_name}' 更新成功")
            return True
            
        except Exception as e:
            logger.error(f"更新提示词失败: {str(e)}")
            return False
    
    def upload_prompts(self, prompts: Dict[str, Dict[str, str]]) -> Dict[str, bool]:
        """
        批量上传提示词到 LangSmith
        
        参数:
            prompts: 提示词字典，格式为 {prompt_name: {"content": "...", "description": "..."}}
            
        返回:
            Dict[str, bool]: 每个提示词的上传结果
        """
        results = {}
        for prompt_name, prompt_data in prompts.items():
            content = prompt_data.get("content", "")
            description = prompt_data.get("description")
            results[prompt_name] = self.upload_prompt(prompt_name, content, description)
        return results
    
    def initialize_default_prompts(self) -> bool:
        """
        初始化默认提示词到 LangSmith
        
        返回:
            bool: 是否全部初始化成功
        """
        default_prompts = {
            "system_prompt": {
                "content": "你是一个乐于助人的AI助手。",
                "description": "系统默认提示词"
            },
            "compression_prompt": {
                "content": "请将以下对话压缩为约1000个token的摘要，保留关键信息和上下文：\n\n",
                "description": "对话压缩提示词"
            },
            "resume_optimization_prompt": {
                "content": """
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
                """,
                "description": "简历优化提示词"
            },
            "interview_preparation_prompt": {
                "content": """
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

## 技能准备和注意事项
[需要准备的技能和面试注意事项，包括行业文化]
                """,
                "description": "面试准备提示词"
            }
        }
        
        results = self.upload_prompts(default_prompts)
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        logger.info(f"初始化默认提示词完成: {success_count}/{total_count} 成功")
        return success_count == total_count

# 创建全局提示词管理服务实例
prompt_manager_service = PromptManagerService()
