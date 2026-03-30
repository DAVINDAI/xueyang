from fastapi import APIRouter, HTTPException, Body, Request
import logging
import json
from app.services.llm import llm_service
from typing import Dict, Any

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()

# 支持的路由类型配置
SUPPORTED_ROUTES = [
    {
        "path": "/chat",
        "name": "对话连接",
        "description": "智能问答、知识查询、聊天对话等"
    },
    {
        "path": "/coding-playground",
        "name": "编码操场",
        "description": "代码编写、编程练习、代码优化等"
    },
    {
        "path": "/notes",
        "name": "笔记管理",
        "description": "笔记创建、查看、搜索、知识管理等"
    },
    {
        "path": "/memo",
        "name": "备忘录",
        "description": "备忘记录、待办事项、重要信息等"
    },
    {
        "path": "/resume",
        "name": "简历优化",
        "description": "简历分析、优化建议、面试准备等"
    },
    {
        "path": "/resume/list",
        "name": "优化历史",
        "description": "简历优化历史、版本记录等"
    },
    {
        "path": "/details",
        "name": "学习详情",
        "description": "学习数据分析、会话统计、学习进度等"
    },
    {
        "path": "/law",
        "name": "法律助手",
        "description": "法律法规查询、法律文件检索、法律咨询等"
    },
    {
        "path": "/assistant",
        "name": "协助助手",
        "description": "任务协助、计划制定、执行支持等"
    },
    {
        "path": "/communication",
        "name": "沟通助手",
        "description": "消息交流、沟通协作等"
    }
]

# 解析提示词
PARSE_PROMPT = """
你是一个智能路由解析助手。你的任务是根据用户的输入内容，判断用户想要访问的功能页面。

## 支持的功能页面

{supported_routes_str}

## 要求

请根据用户输入内容，分析其意图，并返回最合适的页面路由。如果无法确定用户意图，或者用户输入与任何功能页面都不匹配，请返回 `/chat` 路由，因为聊天页面可以处理所有类型的查询。

## 输出格式

只需要返回路由路径（如 `/chat`、`/details` 等），不要返回任何其他信息。

## 用户输入

{user_input}
"""


@router.post("/parse-input", response_model=Dict[str, Any])
async def parse_input(
    request: Request,
    data: Dict[str, Any] = Body(..., description="用户输入数据")
):
    # 支持 inputText 和 input_text 两种字段名
    raw_input_text = data.get("inputText", data.get("input_text", ""))
    logger.info(f"收到原始输入文本类型: {type(raw_input_text)}")
    logger.info(f"收到原始输入文本: {raw_input_text}")
    
    # 打印原始字节值，用于调试编码问题
    logger.info(f"原始字节值: {raw_input_text.encode('utf-8')}")
    
    # 简化编码处理，直接使用UTF-8编码
    # 确保输入文本是有效的UTF-8字符串，避免复杂的编码转换逻辑
    input_text = raw_input_text
    
    # 移除了复杂且易出错的编码转换逻辑，因为FastAPI框架已经在API边界
    # 处理了编码问题，传入的字符串应该已经是有效的UTF-8编码
    """
    解析用户输入并返回对应的路由
    
    根据用户输入内容，智能判断应该路由到哪个页面。如果无法确定，默认返回聊天页面。
    
    - **input_text**: 用户输入的内容
    """
    try:
        # 构建提示词
        supported_routes_str = "\n".join([
            f"- {route['path']} ({route['name']}): {route['description']}"
            for route in SUPPORTED_ROUTES
        ])
        
        prompt = PARSE_PROMPT.format(
            supported_routes_str=supported_routes_str,
            user_input=input_text
        )
        
        # 使用大模型解析
        logger.info(f"开始解析用户输入: {input_text}")
        response = llm_service.generate_completion("qwen-plus", prompt)
        
        # 处理响应
        response = response.strip()
        
        logger.info(f"大模型返回结果: {response}")
        
        # 验证响应是否是有效的路由
        valid_paths = [route['path'] for route in SUPPORTED_ROUTES]
        if response in valid_paths:
            parsed_route = response
        else:
            # 如果响应不是有效的路由，尝试从响应中提取路由
            for route in valid_paths:
                if route in response:
                    parsed_route = route
                    break
            else:
                # 默认返回聊天页面
                logger.warning(f"无法解析用户输入，默认返回聊天页面: {input_text}")
                parsed_route = "/chat"
        
        logger.info(f"解析结果: {parsed_route}")
        
        return {
            "route": parsed_route,
            "query": input_text,
            "confidence": "high"  # 暂时固定为高置信度
        }
        
    except Exception as e:
        logger.error(f"解析用户输入失败: {str(e)}")
        logger.error(logging.traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"解析输入失败: {str(e)}")
