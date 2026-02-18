# 模型配置
MODEL_CONFIGS = {
    "glm-5": {
        "context_length": 1000000,  # 100万token
        "api_base": "https://open.bigmodel.cn/api/paas/v4/",
        "api_key_env": "GLM_API_KEY"
    },
    "qwen-plus": {
        "context_length": 200000,  # 20万token
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "QWEN_API_KEY"
    },
    "deepseek-chat": {
        "context_length": 128000,  # 128k token
        "api_base": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY"
    }
}

# 压缩配置
COMPRESSION_CONFIG = {
    "target_tokens": 1000,  # 压缩目标token数
    "threshold_ratio": 0.8  # 达到上下文长度80%时开始压缩
}

# Tavily API配置
TAVILY_CONFIG = {
    "api_key_env": "TAVILY_API_KEY",
    "base_url": "https://api.tavily.com"
}
