from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.config import MODEL_CONFIGS
from app.services.memory import memory_service
from app.services.tokenizer import tokenizer_service
import os
import time
import logging
from typing import Dict, Any, List, AsyncGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 大模型服务
class LLMService:
    def __init__(self):
        self.llms = {}  # 存储不同模型的实例
        self.streaming_llms = {}  # 存储流式模型的实例
    
    def get_llm(self, model_name: str) -> ChatOpenAI:
        """获取大模型实例"""
        if model_name not in self.llms:
            config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["qwen-plus"])
            api_key = os.getenv(config["api_key_env"])
            
            # 先尝试用 model_name 构造环境变量名，失败则用 config 中的默认值
            api_base_env_name = f"{model_name.upper().replace('-', '_')}_API_BASE"
            api_base = os.getenv(api_base_env_name)
            
            # 如果没有找到，再尝试去掉数字的环境变量名（如 GLM_API_BASE 而不是 GLM_5_API_BASE）
            if not api_base:
                base_name = model_name.split('-')[0].upper()
                api_base_env_name_fallback = f"{base_name}_API_BASE"
                api_base = os.getenv(api_base_env_name_fallback, config["api_base"])
            else:
                api_base = api_base or config["api_base"]
            
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
    
    def get_streaming_llm(self, model_name: str) -> ChatOpenAI:
        """获取流式大模型实例"""
        if model_name not in self.streaming_llms:
            config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["qwen-plus"])
            api_key = os.getenv(config["api_key_env"])
            
            # 先尝试用 model_name 构造环境变量名，失败则用 config 中的默认值
            api_base_env_name = f"{model_name.upper().replace('-', '_')}_API_BASE"
            api_base = os.getenv(api_base_env_name)
            
            # 如果没有找到，再尝试去掉数字的环境变量名（如 GLM_API_BASE 而不是 GLM_5_API_BASE）
            if not api_base:
                base_name = model_name.split('-')[0].upper()
                api_base_env_name_fallback = f"{base_name}_API_BASE"
                api_base = os.getenv(api_base_env_name_fallback, config["api_base"])
            else:
                api_base = api_base or config["api_base"]
            
            # 确保API密钥存在
            if not api_key:
                raise ValueError(f"API key not found for model: {model_name}")
            
            # 创建流式大模型实例
            self.streaming_llms[model_name] = ChatOpenAI(
                model_name=model_name,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=0.7,
                streaming=True
            )
        
        return self.streaming_llms[model_name]
    
    async def chat_stream(self, model_name: str, session_id: str, message: str, messages: List[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """执行流式聊天"""
        try:
            # 获取流式大模型实例
            llm = self.get_streaming_llm(model_name)
            
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
            
            # 获取历史消息（只取最近3个）
            history_messages = []
            if hasattr(memory, 'messages') and memory.messages is not None:
                history_messages = memory.messages[-6:]  # 取最近3轮对话（6条消息：用户+AI）
            
            # 打印历史消息
            logger.info(f"历史消息: {history_messages}")
            # 打印用户消息
            logger.info(f"用户消息: {message}")
            
            # 执行流式对话
            start_time = time.time()
            first_chunk_time = None
            full_response = ""
            
            async for chunk in chain.astream({
                "history": history_messages,
                "input": message
            }):
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    first_token_time = first_chunk_time - start_time
                    logger.info(f"首字耗时: {first_token_time:.2f}秒, 模型: {model_name}")
                
                full_response += chunk
                yield chunk
            
            elapsed_time = time.time() - start_time
            logger.info(f"大模型调用耗时: {elapsed_time:.2f}秒, 模型: {model_name}")

            # 更新记忆
            from langchain_core.messages import HumanMessage, AIMessage
            memory.add_message(HumanMessage(content=message))
            memory.add_message(AIMessage(content=full_response))
            
            # 检查上下文长度
            current_messages = memory_service.save_memory_to_messages(memory)
            # 确保 current_messages 不是 None
            if current_messages is None:
                current_messages = []
            current_tokens = tokenizer_service.count_messages_tokens(model_name, current_messages)
            context_status = tokenizer_service.check_context_length(model_name, current_tokens)
            
            # 如果需要压缩，执行压缩
            if context_status["compression_needed"]:
                logger.info(f"需要压缩上下文, 当前: {current_tokens} tokens")
                # 生成压缩提示
                compression_prompt = tokenizer_service.generate_compression_prompt(current_messages)
                
                # 执行压缩并统计耗时
                compression_start_time = time.time()
                compression_response = chain.invoke({
                    "history": [],
                    "input": compression_prompt
                })
                compression_elapsed_time = time.time() - compression_start_time
                logger.info(f"上下文压缩耗时: {compression_elapsed_time:.2f}秒")
                
                # 清除旧记忆并加载压缩后的内容
                memory_service.clear_session_memory(str(session_id), model_name)
                new_memory = memory_service.get_session_memory(str(session_id), model_name)
                new_memory.add_message(AIMessage(content=compression_response))
            
            logger.info(f"会话 {session_id} 处理完成, 上下文状态: {context_status}")
            
        except Exception as e:
            logger.error(f"聊天错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            yield f"抱歉，发生错误：{str(e)}"
    
    def chat(self, model_name: str, session_id: str, message: str, messages: List[Dict[str, Any]] = None) -> str:
        """执行聊天（非流式）"""
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
            
            # 获取历史消息（只取最近3个）
            history_messages = []
            if hasattr(memory, 'messages') and memory.messages is not None:
                history_messages = memory.messages[-6:]  # 取最近3轮对话（6条消息：用户+AI）
            
            # 执行对话并统计耗时
            start_time = time.time()
            # 打印历史消息
            logger.info(f"历史消息: {history_messages}")
            # 打印用户消息
            logger.info(f"用户消息: {message}")
            response = chain.invoke({
                "history": history_messages,
                "input": message
            })
            elapsed_time = time.time() - start_time
            logger.info(f"大模型调用耗时: {elapsed_time:.2f}秒, 模型: {model_name}")

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
                logger.info(f"需要压缩上下文, 当前: {current_tokens} tokens")
                # 生成压缩提示
                compression_prompt = tokenizer_service.generate_compression_prompt(current_messages)
                
                # 执行压缩并统计耗时
                compression_start_time = time.time()
                compression_response = chain.invoke({
                    "history": [],
                    "input": compression_prompt
                })
                compression_elapsed_time = time.time() - compression_start_time
                logger.info(f"上下文压缩耗时: {compression_elapsed_time:.2f}秒")
                
                # 清除旧记忆并加载压缩后的内容
                memory_service.clear_session_memory(str(session_id), model_name)
                new_memory = memory_service.get_session_memory(str(session_id), model_name)
                new_memory.add_message(AIMessage(content=compression_response))
            
            logger.info(f"会话 {session_id} 处理完成, 上下文状态: {context_status}")
            
            return response
        except Exception as e:
            logger.error(f"聊天错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"抱歉，发生错误：{str(e)}"
    
    def generate_completion(self, model_name: str, prompt: str) -> str:
        """生成文本完成"""
        try:
            llm = self.get_llm(model_name)
            start_time = time.time()
            response = llm.invoke(prompt)
            elapsed_time = time.time() - start_time
            logger.info(f"文本完成调用耗时: {elapsed_time:.2f}秒, 模型: {model_name}")
            return response.content
        except Exception as e:
            logger.error(f"文本完成错误: {str(e)}")
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
