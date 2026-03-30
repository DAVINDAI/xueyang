from fastapi import APIRouter, HTTPException, Body, Request
import traceback
import logging
import json
from app.services.db import (
    create_communication_message,
    get_communication_messages,
    get_communication_message,
    update_communication_message_status,
    delete_communication_message,
    create_response_suggestion,
    get_response_suggestions_by_message,
    delete_response_suggestions_by_message,
    create_user_role,
    get_user_roles,
    get_user_role,
    update_user_role,
    delete_user_role
)
from app.services.llm import llm_service
from app.services.tokenizer import tokenizer_service
from app.config import MODEL_CONFIGS
from app.api.auth import USER_ACCOUNTS
from typing import Dict, Any, List

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()

# 获取用户列表
@router.get("/users", response_model=List[Dict[str, Any]])
async def get_users():
    """
    获取用户列表
    
    返回所有可用用户的列表，包含用户名和角色信息。
    """
    return [
        {"username": user["username"], "role": user["role"]}
        for user in USER_ACCOUNTS
    ]

# 消息润色
@router.post("/polish", response_model=Dict[str, Any])
async def polish_message(
    request: Request,
    sender_id: str = Body(..., description="发送者ID"),
    receiver_id: str = Body(..., description="接收者ID"),
    original_content: str = Body(..., description="原始消息内容"),
    sender_role: str = Body(..., description="发送者角色"),
    receiver_role: str = Body(..., description="接收者角色"),
    model_name: str = Body("qwen-plus", description="模型名称")
):
    """
    润色消息
    
    使用大模型对原始消息进行润色，提高沟通效果。
    
    - **sender_id**: 发送者ID
    - **receiver_id**: 接收者ID
    - **original_content**: 原始消息内容
    - **sender_role**: 发送者角色
    - **receiver_role**: 接收者角色
    - **model_name**: 模型名称，可选值：glm-5, qwen-plus
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 构建润色提示词
        polish_prompt = f"""
你是一个专业的沟通助手，擅长根据不同角色和场景优化沟通内容。

请根据以下信息，对原始消息进行润色：

- 发送者角色：{sender_role}
- 接收者角色：{receiver_role}
- 原始消息：{original_content}

润色要求：
1. 保持原始消息的核心内容不变
2. 语言更加专业、得体
3. 语气符合发送者的角色定位
4. 考虑接收者的角色，确保沟通效果
5. 长度适中，不要过长

请直接返回润色后的消息，不要添加任何解释或说明。
        """
        
        # 调用大模型进行润色
        polished_content = llm_service.chat(model_name, None, polish_prompt, [])
        
        # 计算token数
        token_count = tokenizer_service.count_tokens(model_name, polished_content)
        
        return {
            "polished_content": polished_content,
            "token_count": token_count
        }
    except Exception as e:
        logger.error(f"润色消息失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"润色消息失败: {str(e)}")

# 发送消息
@router.post("/messages", response_model=Dict[str, Any])
async def send_message(
    request: Request,
    sender_id: str = Body(..., description="发送者ID"),
    receiver_id: str = Body(..., description="接收者ID"),
    original_content: str = Body(..., description="原始消息内容"),
    polished_content: str = Body(..., description="润色后的消息内容"),
    sender_role: str = Body(..., description="发送者角色"),
    receiver_role: str = Body(..., description="接收者角色")
):
    """
    发送消息
    
    保存并发送沟通消息。
    
    - **sender_id**: 发送者ID
    - **receiver_id**: 接收者ID
    - **original_content**: 原始消息内容
    - **polished_content**: 润色后的消息内容
    - **sender_role**: 发送者角色
    - **receiver_role**: 接收者角色
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 创建沟通消息
        message_id = create_communication_message(
            visitor_id, 
            sender_id, 
            receiver_id, 
            original_content, 
            polished_content, 
            sender_role, 
            receiver_role
        )
        
        # 更新消息状态为已发送
        update_communication_message_status(visitor_id, message_id, 'sent')
        
        return {
            "message_id": message_id,
            "status": "sent"
        }
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

# 获取消息列表
@router.get("/messages", response_model=List[Dict[str, Any]])
async def list_messages(
    request: Request,
    user_id: str = None,
    role: str = None,
    limit: int = 20,
    offset: int = 0
):
    """
    获取消息列表
    
    返回沟通消息列表，可按用户ID和角色筛选。
    
    - **user_id**: 用户ID（可选）
    - **role**: 角色类型（sender/receiver，可选）
    - **limit**: 限制数量（默认20）
    - **offset**: 偏移量（默认0）
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        messages = get_communication_messages(visitor_id, user_id, role, limit, offset)
        return messages
    except Exception as e:
        logger.error(f"获取消息列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取消息列表失败: {str(e)}")

# 获取消息详情
@router.get("/messages/{message_id}", response_model=Dict[str, Any])
async def get_message(
    request: Request,
    message_id: int
):
    """
    获取消息详情
    
    返回指定消息的详细信息，包括原始消息、润色后的消息和回复建议。
    
    - **message_id**: 消息ID
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 获取消息详情
        message = get_communication_message(visitor_id, message_id)
        if not message:
            raise HTTPException(status_code=404, detail=f"消息不存在: {message_id}")
        
        # 获取回复建议
        suggestions = get_response_suggestions_by_message(visitor_id, message_id)
        
        # 按类型分组建议
        reply_suggestions = [s for s in suggestions if s['suggestion_type'] == 'reply']
        action_suggestions = [s for s in suggestions if s['suggestion_type'] == 'action']
        
        return {
            **message,
            "reply_suggestions": reply_suggestions,
            "action_suggestions": action_suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息详情失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取消息详情失败: {str(e)}")

# 删除消息
@router.delete("/messages/{message_id}", response_model=Dict[str, Any])
async def delete_message(
    request: Request,
    message_id: int
):
    """
    删除消息
    
    删除指定的沟通消息及其相关的回复建议。
    
    - **message_id**: 消息ID
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        deleted = delete_communication_message(visitor_id, message_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"消息不存在: {message_id}")
        return {
            "message_id": message_id,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除消息失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")

# 获取回复建议
@router.post("/suggestions", response_model=Dict[str, Any])
async def get_suggestions(
    request: Request,
    message_id: int = Body(..., description="消息ID"),
    receiver_role: str = Body(..., description="接收者角色"),
    model_name: str = Body("qwen-plus", description="模型名称")
):
    """
    获取回复建议
    
    基于接收者角色，为指定消息生成回复建议和行动建议。
    
    - **message_id**: 消息ID
    - **receiver_role**: 接收者角色
    - **model_name**: 模型名称，可选值：glm-5, qwen-plus
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        
        # 获取消息详情
        message = get_communication_message(visitor_id, message_id)
        if not message:
            raise HTTPException(status_code=404, detail=f"消息不存在: {message_id}")
        
        # 构建回复建议提示词
        suggestion_prompt = f"""
你是一个专业的沟通助手，擅长根据不同角色和场景提供合适的回复建议。

请根据以下信息，为接收者生成回复建议和行动建议：

- 发送者角色：{message['sender_role']}
- 接收者角色：{receiver_role}
- 原始消息：{message['original_content']}
- 润色后的消息：{message['polished_content']}

请生成：
1. 3条回复建议，语气符合接收者角色，内容针对消息内容
2. 2条行动建议，基于接收者角色，提供具体的行动步骤

输出格式：
回复建议：
1. 建议1内容
2. 建议2内容
3. 建议3内容

行动建议：
1. 行动1内容
2. 行动2内容
        """
        
        # 调用大模型生成建议
        suggestions_text = llm_service.chat(model_name, None, suggestion_prompt, [])
        
        # 解析建议
        reply_suggestions = []
        action_suggestions = []
        
        lines = suggestions_text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('回复建议：'):
                current_section = 'reply'
            elif line.startswith('行动建议：'):
                current_section = 'action'
            elif line and current_section:
                if line.startswith('1. '):
                    content = line[3:].strip()
                    if current_section == 'reply':
                        reply_suggestions.append(content)
                    else:
                        action_suggestions.append(content)
                elif line.startswith('2. '):
                    content = line[3:].strip()
                    if current_section == 'reply':
                        reply_suggestions.append(content)
                    else:
                        action_suggestions.append(content)
                elif line.startswith('3. '):
                    content = line[3:].strip()
                    if current_section == 'reply':
                        reply_suggestions.append(content)
        
        # 保存回复建议
        for i, suggestion in enumerate(reply_suggestions):
            create_response_suggestion(visitor_id, message_id, 'reply', suggestion, 1.0 - i * 0.1)
        
        # 保存行动建议
        for i, suggestion in enumerate(action_suggestions):
            create_response_suggestion(visitor_id, message_id, 'action', suggestion, 1.0 - i * 0.1)
        
        return {
            "reply_suggestions": reply_suggestions,
            "action_suggestions": action_suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回复建议失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取回复建议失败: {str(e)}")

# 角色管理

@router.post("/roles", response_model=Dict[str, Any])
async def create_role(
    request: Request,
    role_name: str = Body(..., description="角色名称"),
    description: str = Body(None, description="角色描述")
):
    """
    创建用户角色
    
    - **role_name**: 角色名称
    - **description**: 角色描述（可选）
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        role_id = create_user_role(visitor_id, role_name, description)
        return {
            "role_id": role_id,
            "role_name": role_name,
            "description": description
        }
    except Exception as e:
        logger.error(f"创建角色失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"创建角色失败: {str(e)}")

@router.get("/roles", response_model=List[Dict[str, Any]])
async def list_roles(request: Request):
    """
    获取所有用户角色
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        roles = get_user_roles(visitor_id)
        return roles
    except Exception as e:
        logger.error(f"获取角色列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取角色列表失败: {str(e)}")

@router.get("/roles/{role_name}", response_model=Dict[str, Any])
async def get_role(
    request: Request,
    role_name: str
):
    """
    获取单个用户角色
    
    - **role_name**: 角色名称
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        role = get_user_role(visitor_id, role_name)
        if not role:
            raise HTTPException(status_code=404, detail=f"角色不存在: {role_name}")
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取角色失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取角色失败: {str(e)}")

@router.put("/roles/{role_name}", response_model=Dict[str, Any])
async def update_role(
    request: Request,
    role_name: str,
    description: str = Body(..., description="角色描述")
):
    """
    更新用户角色
    
    - **role_name**: 角色名称
    - **description**: 角色描述
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        updated = update_user_role(visitor_id, role_name, description)
        if not updated:
            raise HTTPException(status_code=404, detail=f"角色不存在: {role_name}")
        return {
            "role_name": role_name,
            "description": description,
            "updated": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新角色失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"更新角色失败: {str(e)}")

@router.delete("/roles/{role_name}", response_model=Dict[str, Any])
async def delete_role(
    request: Request,
    role_name: str
):
    """
    删除用户角色
    
    - **role_name**: 角色名称
    """
    try:
        visitor_id = getattr(request.state, 'visitor_id', None)
        deleted = delete_user_role(visitor_id, role_name)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"角色不存在: {role_name}")
        return {
            "role_name": role_name,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除角色失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"删除角色失败: {str(e)}")
