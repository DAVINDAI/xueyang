from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.config import MODEL_CONFIGS
from app.services.memory import memory_service
from app.services.tokenizer import tokenizer_service
import os
from typing import Dict, Any, List

# 大模型服务
class LLMService:
    def __init__(self):
        self.llms = {}  # 存储不同模型的实例
    
    def get_llm(self, model_name: str) -> ChatOpenAI:
        """获取大模型实例"""
        if model_name not in self.llms:
            config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["qwen-plus"])
            api_key = os.getenv(config["api_key_env"])
            api_base = os.getenv(f"{model_name.upper().replace('-', '_')}_API_BASE", config["api_base"])
            
            # 确保API密钥存在
            if not api_key:
                raise ValueError(f"API key not found for model: {model_name}")
            
            # 创建大模型实例
            self.llms[model_name] = ChatOpenAI(
                model_name=model_name,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=0.7
            )
        
        return self.llms[model_name]
    
    def chat(self, model_name: str, session_id: str, message: str, messages: List[Dict[str, Any]] = None) -> str:
        """执行聊天"""
        try:
            # 获取大模型实例
            llm = self.get_llm(model_name)
            
            # 获取会话记忆
            memory = memory_service.get_session_memory(str(session_id), model_name)
            
            # 如果提供了消息列表，加载到记忆中
            if messages:
                memory_service.load_memory_from_messages(memory, messages)
            
            # 使用 LCEL 构建对话链
            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个乐于助人的AI助手。"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
            
            chain = prompt | llm | StrOutputParser()
            
            # 获取历史消息（确保是可迭代的）
            history_messages = []
            if hasattr(memory, 'messages') and memory.messages is not None:
                history_messages = memory.messages
            
            # 执行对话
            response = chain.invoke({
                "history": history_messages,
                "input": message
            })
            
            # 更新记忆
            from langchain_core.messages import HumanMessage, AIMessage
            memory.add_message(HumanMessage(content=message))
            memory.add_message(AIMessage(content=response))
            
            # 检查上下文长度
            current_messages = memory_service.save_memory_to_messages(memory)
            # 确保 current_messages 不是 None
            if current_messages is None:
                current_messages = []
            current_tokens = tokenizer_service.count_messages_tokens(model_name, current_messages)
            context_status = tokenizer_service.check_context_length(model_name, current_tokens)
            
            # 如果需要压缩，执行压缩
            if context_status["compression_needed"]:
                # 生成压缩提示
                compression_prompt = tokenizer_service.generate_compression_prompt(current_messages)
                
                # 执行压缩
                compression_response = chain.invoke({
                    "history": [],
                    "input": compression_prompt
                })
                
                # 清除旧记忆并加载压缩后的内容
                memory_service.clear_session_memory(str(session_id), model_name)
                new_memory = memory_service.get_session_memory(str(session_id), model_name)
                new_memory.add_message(AIMessage(content=compression_response))
            
            return response
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"抱歉，发生错误：{str(e)}"
    
    def generate_completion(self, model_name: str, prompt: str) -> str:
        """生成文本完成"""
        try:
            llm = self.get_llm(model_name)
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error in completion: {str(e)}")
            return f"抱歉，发生错误：{str(e)}"
    
    def clear_llm(self, model_name: str):
        """清除大模型实例"""
        if model_name in self.llms:
            del self.llms[model_name]
    
    def clear_all(self):
        """清除所有大模型实例"""
        self.llms.clear()

# 创建全局大模型服务实例
llm_service = LLMService()
