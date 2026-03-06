import tiktoken
from app.config import MODEL_CONFIGS, COMPRESSION_CONFIG
from typing import List, Dict, Any

# Token计算服务
class TokenizerService:
    def __init__(self):
        self.tokenizers = {}
        self._initialize_tokenizers()
    
    def _initialize_tokenizers(self):
        """初始化tokenizer"""
        # 为不同模型初始化tokenizer
        try:
            # GLM 5 使用 cl100k_base
            self.tokenizers["glm-5"] = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # 回退到默认tokenizer
            self.tokenizers["glm-5"] = tiktoken.get_encoding("gpt2")
        
        try:
            # Qwen Plus 使用 cl100k_base
            self.tokenizers["qwen-plus"] = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # 回退到默认tokenizer
            self.tokenizers["qwen-plus"] = tiktoken.get_encoding("gpt2")
        
        try:
            # DeepSeek Chat 使用 cl100k_base
            self.tokenizers["deepseek-chat"] = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # 回退到默认tokenizer
            self.tokenizers["deepseek-chat"] = tiktoken.get_encoding("gpt2")
    
    def count_tokens(self, model_name: str, text: str) -> int:
        """计算文本的token数量"""
        tokenizer = self.tokenizers.get(model_name, self.tokenizers.get("qwen-plus"))
        return len(tokenizer.encode(text))
    
    def count_messages_tokens(self, model_name: str, messages: List[Dict[str, Any]]) -> int:
        """计算消息列表的总token数量"""
        total_tokens = 0
        if messages is not None:
            for message in messages:
                if message is None:
                    continue
                content = message.get("content", "")
                total_tokens += self.count_tokens(model_name, content)
        return total_tokens
    
    def check_context_length(self, model_name: str, current_tokens: int) -> Dict[str, Any]:
        """检查上下文长度是否超出限制"""
        config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["qwen-plus"])
        context_length = config.get("context_length", 200000)
        
        threshold = int(context_length * COMPRESSION_CONFIG["threshold_ratio"])
        target_tokens = COMPRESSION_CONFIG["target_tokens"]
        
        is_over_threshold = current_tokens >= threshold
        is_over_limit = current_tokens >= context_length
        
        return {
            "current_tokens": current_tokens,
            "context_length": context_length,
            "threshold": threshold,
            "is_over_threshold": is_over_threshold,
            "is_over_limit": is_over_limit,
            "target_tokens": target_tokens,
            "compression_needed": is_over_threshold
        }
    
    def generate_compression_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """生成压缩提示"""
        prompt = "请将以下对话压缩为约1000个token的摘要，保留关键信息和上下文：\n\n"
        
        if messages is not None:
            for message in messages:
                if message is None:
                    continue
                role = "用户" if message.get("role") == "user" else "助手"
                content = message.get("content", "")
                prompt += f"{role}: {content}\n\n"
        
        prompt += "摘要："
        return prompt
    
    def truncate_messages(self, model_name: str, messages: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        """截断消息以适应最大token数"""
        truncated_messages = []
        total_tokens = 0
        
        if messages is None:
            return truncated_messages
        
        # 从最新的消息开始保留
        for message in reversed(messages):
            if message is None:
                continue
            message_tokens = self.count_tokens(model_name, message.get("content", ""))
            
            if total_tokens + message_tokens <= max_tokens:
                truncated_messages.insert(0, message)
                total_tokens += message_tokens
            else:
                # 消息过长，截断内容
                content = message.get("content", "")
                tokenizer = self.tokenizers.get(model_name, self.tokenizers.get("qwen-plus"))
                tokens = tokenizer.encode(content)
                remaining_tokens = max_tokens - total_tokens
                
                if remaining_tokens > 0:
                    truncated_content = tokenizer.decode(tokens[:remaining_tokens])
                    truncated_message = message.copy()
                    truncated_message["content"] = truncated_content
                    truncated_messages.insert(0, truncated_message)
                    total_tokens += remaining_tokens
                
                break
        
        return truncated_messages

# 创建全局tokenizer服务实例
tokenizer_service = TokenizerService()
