import autogen
import requests
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoGenService:
    def __init__(self):
        # 配置 AutoGen 模型
        self.config_list = [
            {
                "model": "doubao-seed-1-8-251228",
                "api_key": "6eaae36f-0c38-4117-a13d-eb59d18c92e1",
                "base_url": "https://ark.cn-beijing.volces.com/api/v3"
            }
        ]
        
        # 创建五个角色
        self.user_experience_officer = autogen.AssistantAgent(
            name="UserExperienceOfficer",
            system_message="你是一位专业的用户体验官，负责分析网站的用户体验，识别问题并提供优化建议。你会访问网站，评估其易用性、导航结构、内容布局等方面，并生成详细的用户体验报告。",
            llm_config={"config_list": self.config_list}
        )
        
        self.interaction_designer = autogen.AssistantAgent(
            name="InteractionDesigner",
            system_message="你是一位专业的交互设计师，负责设计网站的交互流程和用户界面元素。你会根据用户体验官的建议，设计更直观、更高效的交互方案，包括按钮位置、导航结构、表单设计等。",
            llm_config={"config_list": self.config_list}
        )
        
        self.visual_designer = autogen.AssistantAgent(
            name="VisualDesigner",
            system_message="你是一位专业的视觉设计师，负责网站的视觉风格和美学设计。你会根据用户体验官和交互设计师的建议，设计更美观、更一致的视觉方案，包括颜色方案、排版、图标设计等。",
            llm_config={"config_list": self.config_list}
        )
        
        self.frontend_engineer = autogen.AssistantAgent(
            name="FrontendEngineer",
            system_message="你是一位专业的前端工程师，负责实现网站的前端代码。你会根据交互设计师和视觉设计师的方案，编写高质量的前端代码，确保网站的功能和美观性。",
            llm_config={"config_list": self.config_list}
        )
        
        self.backend_engineer = autogen.AssistantAgent(
            name="BackendEngineer",
            system_message="你是一位专业的后端工程师，负责实现网站的后端功能。你会根据前端工程师的需求，编写高质量的后端代码，确保网站的性能和安全性。",
            llm_config={"config_list": self.config_list}
        )
        
        # 创建用户代理
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            system_message="你是项目的协调者，负责引导各个角色的工作，确保他们按照正确的顺序协作，并最终生成完整的优化方案。",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            llm_config={"config_list": self.config_list},
            code_execution_config={"use_docker": False}
        )
    
    def access_website(self, url: str) -> str:
        """访问网站并获取内容"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"访问网站失败: {str(e)}")
            return f"访问网站失败: {str(e)}"
    
    def generate_evolution_suggestions(self) -> Dict[str, Any]:
        """生成网站进化建议"""
        try:
            # 访问 xueyang.me
            logger.info("正在访问 xueyang.me...")
            website_content = self.access_website("http://xueyang.me")
            
            # 任务 1: 用户体验官分析网站
            logger.info("用户体验官正在分析网站...")
            uxo_message = f"请分析以下网站的用户体验，并提供详细的优化建议：\n{website_content[:5000]}"
            
            # 任务 2: 交互设计师提供交互设计建议
            logger.info("交互设计师正在提供交互设计建议...")
            id_message = f"基于用户体验官的分析，请提供详细的交互设计优化建议。"
            
            # 任务 3: 视觉设计师提供视觉设计建议
            logger.info("视觉设计师正在提供视觉设计建议...")
            vd_message = f"基于用户体验官和交互设计师的分析，请提供详细的视觉设计优化建议。"
            
            # 任务 4: 前端工程师提供前端实现建议
            logger.info("前端工程师正在提供前端实现建议...")
            fe_message = f"基于交互设计师和视觉设计师的建议，请提供详细的前端实现方案。"
            
            # 任务 5: 后端工程师提供后端实现建议
            logger.info("后端工程师正在提供后端实现建议...")
            be_message = f"基于前端工程师的需求，请提供详细的后端实现方案。"
            
            # 执行对话
            logger.info("开始执行角色协作...")
            
            # 先让用户体验官分析网站
            uxo_result = self.user_proxy.initiate_chat(
                self.user_experience_officer,
                message=uxo_message,
                summary_method="last_msg"
            )
            
            # 然后让交互设计师提供建议
            id_result = self.user_proxy.initiate_chat(
                self.interaction_designer,
                message=f"用户体验官的分析结果：{uxo_result.summary}\n{id_message}",
                summary_method="last_msg"
            )
            
            # 然后让视觉设计师提供建议
            vd_result = self.user_proxy.initiate_chat(
                self.visual_designer,
                message=f"用户体验官的分析结果：{uxo_result.summary}\n交互设计师的建议：{id_result.summary}\n{vd_message}",
                summary_method="last_msg"
            )
            
            # 然后让前端工程师提供实现方案
            fe_result = self.user_proxy.initiate_chat(
                self.frontend_engineer,
                message=f"交互设计师的建议：{id_result.summary}\n视觉设计师的建议：{vd_result.summary}\n{fe_message}",
                summary_method="last_msg"
            )
            
            # 最后让后端工程师提供实现方案
            be_result = self.user_proxy.initiate_chat(
                self.backend_engineer,
                message=f"前端工程师的需求：{fe_result.summary}\n{be_message}",
                summary_method="last_msg"
            )
            
            # 生成最终的进化建议
            final_result = {
                "user_experience": uxo_result.summary,
                "interaction_design": id_result.summary,
                "visual_design": vd_result.summary,
                "frontend_implementation": fe_result.summary,
                "backend_implementation": be_result.summary,
                "overall_suggestions": "\n".join([
                    uxo_result.summary,
                    id_result.summary,
                    vd_result.summary,
                    fe_result.summary,
                    be_result.summary
                ])
            }
            
            logger.info(f"网站进化建议生成完成，建议内容：{final_result}")
            return final_result
            
        except Exception as e:
            logger.error(f"生成进化建议失败: {str(e)}")
            return {
                "error": str(e),
                "message": "生成进化建议失败"
            }

# 创建全局 AutoGen 服务实例
autogen_service = AutoGenService()