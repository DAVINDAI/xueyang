from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any

# 记忆服务
class MemoryService:
    def __init__(self):
        self.memories = {}  # 存储不同会话的记忆实例
    
    def get_memory(self, memory_type: str = 'in_memory', **kwargs) -> Any:
        """获取适合的记忆组件"""
        return InMemoryChatMessageHistory()
    
    def get_session_memory(self, session_id: str, model_name: str, **kwargs) -> Any:
        """获取会话的记忆实例"""
        memory_key = f"{session_id}_{model_name}"
        
        if memory_key not in self.memories:
            self.memories[memory_key] = self.get_memory()
        
        return self.memories[memory_key]
    
    def load_memory_from_messages(self, memory: Any, messages: List[Dict[str, Any]]):
        """从消息列表加载记忆"""
        if hasattr(memory, 'messages') and messages is not None:
            memory.clear()
            for msg in messages:
                if not msg:
                    continue
                role = msg.get('role')
                content = msg.get('content', '')
                
                if role == 'user':
                    memory.add_message(HumanMessage(content=content))
                elif role == 'assistant':
                    memory.add_message(AIMessage(content=content))
    
    def save_memory_to_messages(self, memory: Any) -> List[Dict[str, Any]]:
        """将记忆保存为消息列表"""
        if hasattr(memory, 'messages'):
            messages = []
            memory_messages = memory.messages
            if memory_messages is not None:
                for msg in memory_messages:
                    if not msg:
                        continue
                    msg_dict = {}
                    
                    if hasattr(msg, 'content'):
                        msg_dict['content'] = msg.content
                    
                    if hasattr(msg, 'type'):
                        if msg.type == 'human':
                            msg_dict['role'] = 'user'
                        elif msg.type == 'ai':
                            msg_dict['role'] = 'assistant'
                    
                    if msg_dict:
                        messages.append(msg_dict)
            
            return messages
        
        return []
    
    def clear_session_memory(self, session_id: str, model_name: str):
        """清除会话的记忆"""
        memory_key = f"{session_id}_{model_name}"
        if memory_key in self.memories:
            self.memories[memory_key].clear()
    
    def clear_all_memories(self):
        """清除所有记忆"""
        for memory in self.memories.values():
            if hasattr(memory, 'clear'):
                memory.clear()
        self.memories.clear()

# 创建全局记忆服务实例
memory_service = MemoryService()
