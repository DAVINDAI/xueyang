from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
import traceback
import logging
import json
import asyncio
from app.services.db import (
    create_chat_session,
    get_chat_sessions,
    get_chat_session,
    update_chat_session,
    delete_chat_session,
    save_chat_message,
    get_chat_messages,
    delete_chat_message,
    create_memo_message,
    get_memo_messages,
    get_memo_message,
    get_memo_messages_by_session,
    delete_memo_message
)
from app.services.llm import llm_service
from app.services.tokenizer import tokenizer_service
from app.config import MODEL_CONFIGS
from typing import Dict, Any, List

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()

# 备忘录辅助方法
async def process_memo_command(session_id: int, model_name: str, user_message_id: int) -> Dict[str, Any]:
    """
    处理备忘录命令，创建备忘录
    
    Args:
        session_id: 会话ID
        model_name: 模型名称
        user_message_id: 当前用户消息ID
        
    Returns:
        dict: 包含备忘录创建结果的字典
    """
    # 获取会话的所有消息（包含刚保存的消息）
    current_messages = get_chat_messages(session_id)
    if len(current_messages) < 3:  # 需要至少有一条之前的用户消息和AI回复
        raise HTTPException(status_code=400, detail="会话消息不足，无法创建备忘录")
    
    # 构建分析提示
    last_three_messages = current_messages[-3:]
    user_message = None
    ai_message = None
    
    for msg in last_three_messages:
        if msg['role'] == 'user' and msg['id'] != user_message_id:
            user_message = msg
        elif msg['role'] == 'assistant':
            ai_message = msg
    
    if not user_message or not ai_message:
        raise HTTPException(status_code=400, detail="无法找到上一轮对话消息")
    
    # 构建分析提示
    analysis_prompt = f"""
你是一个专业的对话分析助手。请将以下原始对话记录，按话题转换成一个清晰的列表。
每个列表项包含：主题、用户问题/陈述、AI回复的核心要点。
确保提取所有技术术语、方法、结论和推荐资源。

**对话记录：**
用户：{user_message['content']}
AI：{ai_message['content']}

**输出格式要求（必须严格遵守）：**
{{
  "topics": [
    {{
      "topic": "主题名称",
      "user_question": "用户的问题或陈述",
      "ai_key_points": [
        "要点1",
        "要点2"
      ],
      "technical_terms": ["术语1", "术语2"],
      "methods": ["方法1"],
      "conclusions": ["结论1"],
      "resources": ["资源1"]
    }}
  ]
}}

**重要：**
- 必须返回有效的 JSON 格式
- 必须使用上述字段名
- 必须包含 "topics" 字段
- 不要返回任何其他格式或解释文本
- 只返回 JSON，不要包含其他任何内容
            """
    
    # 使用大模型提取关键信息
    analysis_result = await llm_service.agenerate_completion(model_name, analysis_prompt)
    
    # 清理结果
    if analysis_result.startswith('```json'):
        analysis_result = analysis_result[7:]
    if analysis_result.startswith('```'):
        analysis_result = analysis_result[3:]
    if analysis_result.endswith('```'):
        analysis_result = analysis_result[:-3]
    analysis_result = analysis_result.strip()
    
    # 解析 JSON
    try:
        analysis_data = json.loads(analysis_result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="大模型返回的结果不是有效的 JSON 格式")
    
    # 保存备忘录
    memo_id = create_memo_message(session_id, user_message['id'], json.dumps(analysis_data, ensure_ascii=False))
    
    return {
        "session_id": session_id,
        "model_name": model_name,
        "user_message_id": user_message_id,
        "memo_id": memo_id,
        "analysis": analysis_data
    }

# 会话管理

@router.post("/sessions", response_model=Dict[str, Any])
async def create_session(
    session_name: str = Body(..., description="会话名称"),
    model_name: str = Body(..., description="模型名称", enum=list(MODEL_CONFIGS.keys()))
):
    """
    创建聊天会话
    
    创建一个新的聊天会话，指定会话名称和使用的模型。
    
    - **session_name**: 会话名称
    - **model_name**: 模型名称，可选值：glm-5, qwen-plus
    """
    try:
        session_id = create_chat_session(session_name, model_name)
        return {
            "session_id": session_id,
            "session_name": session_name,
            "model_name": model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_sessions():
    """
    获取会话列表
    
    返回所有聊天会话的列表。
    """
    try:
        sessions = get_chat_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: int):
    """
    获取会话信息
    
    返回指定会话的详细信息。
    
    - **session_id**: 会话ID
    """
    try:
        session = get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话信息失败: {str(e)}")

@router.put("/sessions/{session_id}", response_model=Dict[str, Any])
async def update_session(
    session_id: int,
    session_name: str = Body(..., description="新的会话名称")
):
    """
    更新会话信息
    
    更新指定会话的名称。
    
    - **session_id**: 会话ID
    - **session_name**: 新的会话名称
    """
    try:
        updated = update_chat_session(session_id, session_name)
        if not updated:
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        return {
            "session_id": session_id,
            "session_name": session_name,
            "updated": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新会话失败: {str(e)}")

@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def delete_session(session_id: int):
    """
    删除会话
    
    删除指定的聊天会话及其所有消息。
    
    - **session_id**: 会话ID
    """
    try:
        deleted = delete_chat_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        return {
            "session_id": session_id,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")

# 消息管理

@router.get("/messages/{session_id}", response_model=List[Dict[str, Any]])
async def get_messages(session_id: int):
    """
    获取会话消息
    
    返回指定会话的所有消息。
    
    - **session_id**: 会话ID
    """
    try:
        messages = get_chat_messages(session_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")

@router.delete("/messages/{message_id}", response_model=Dict[str, Any])
async def delete_message(message_id: int):
    """
    删除消息
    
    删除指定的聊天消息。
    
    - **message_id**: 消息ID
    """
    try:
        deleted = delete_chat_message(message_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"消息不存在: {message_id}")
        return {
            "message_id": message_id,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")

# 聊天功能

@router.post("/completion", response_model=Dict[str, Any])
async def chat_completion(
    session_id: int = Body(..., description="会话ID"),
    model_name: str = Body(..., description="模型名称", enum=list(MODEL_CONFIGS.keys())),
    message: str = Body(..., description="用户消息")
):
    """
    大模型聊天
    
    使用指定的模型生成对用户消息的回复。
    
    - **session_id**: 会话ID
    - **model_name**: 模型名称，可选值：glm-5, qwen-plus
    - **message**: 用户消息内容
    """
    try:
        # 检查会话是否存在
        session = get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        
        # 获取历史消息
        messages = get_chat_messages(session_id)
        
        # 计算用户消息的token数
        user_token_count = tokenizer_service.count_tokens(model_name, message)
        
        # 保存用户消息
        user_message_id = save_chat_message(session_id, "user", message, user_token_count)
        
        # 检查是否为备忘录命令
        if message == '记一下' or message == 'm':
            memo_result = await process_memo_command(session_id, model_name, user_message_id)
            memo_result["message"] = "备忘录创建成功"
            return memo_result
        
        # 执行聊天
        response = llm_service.chat(model_name, session_id, message, messages)
        
        # 计算AI回复的token数
        ai_token_count = tokenizer_service.count_tokens(model_name, response)
        
        # 保存AI回复
        ai_message_id = save_chat_message(session_id, "assistant", response, ai_token_count)
        
        # 检查上下文长度
        current_messages = get_chat_messages(session_id)
        current_tokens = tokenizer_service.count_messages_tokens(model_name, current_messages)
        context_status = tokenizer_service.check_context_length(model_name, current_tokens)
        
        return {
            "session_id": session_id,
            "model_name": model_name,
            "user_message_id": user_message_id,
            "ai_message_id": ai_message_id,
            "response": response,
            "context_status": context_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天错误: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@router.post("/completion/stream")
async def chat_completion_stream(
    session_id: int = Body(..., description="会话ID"),
    model_name: str = Body(..., description="模型名称", enum=list(MODEL_CONFIGS.keys())),
    message: str = Body(..., description="用户消息")
):
    """
    大模型聊天（流式输出）
    
    使用指定的模型生成对用户消息的回复，支持流式输出。
    
    - **session_id**: 会话ID
    - **model_name**: 模型名称，可选值：glm-5, qwen-plus
    - **message**: 用户消息内容
    """
    try:
        # 检查会话是否存在
        session = get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        
        # 获取历史消息
        messages = get_chat_messages(session_id)
        
        # 计算用户消息的token数
        user_token_count = tokenizer_service.count_tokens(model_name, message)
        
        # 保存用户消息
        user_message_id = save_chat_message(session_id, "user", message, user_token_count)
        
        # 检查是否为备忘录命令
        if message == '记一下' or message == 'm':
            memo_result = await process_memo_command(session_id, model_name, user_message_id)
            
            async def generate_memo_response():
                yield f"data: {json.dumps({'type': 'chunk', 'content': '备忘录创建成功'}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
                yield f"data: {json.dumps({'type': 'done', 'user_message_id': user_message_id, 'memo_id': memo_result['memo_id'], 'message': '备忘录创建成功', 'analysis': memo_result['analysis']}, ensure_ascii=False)}\n\n"
            
            return StreamingResponse(
                generate_memo_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    "Transfer-Encoding": "chunked"
                }
            )
        
        async def generate():
            full_response = ""
            first_chunk = True
            async for chunk in llm_service.chat_stream(model_name, session_id, message, messages):
                full_response += chunk
                if first_chunk:
                    logger.info(f"收到第一个 chunk，长度: {len(chunk)}")
                    first_chunk = False
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0)
            
            ai_token_count = tokenizer_service.count_tokens(model_name, full_response)
            ai_message_id = save_chat_message(session_id, "assistant", full_response, ai_token_count)
            
            current_messages = get_chat_messages(session_id)
            current_tokens = tokenizer_service.count_messages_tokens(model_name, current_messages)
            context_status = tokenizer_service.check_context_length(model_name, current_tokens)
            
            yield f"data: {json.dumps({'type': 'done', 'user_message_id': user_message_id, 'ai_message_id': ai_message_id, 'context_status': context_status}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Transfer-Encoding": "chunked"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天错误: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")

# 配置信息

@router.get("/config", response_model=Dict[str, Any])
async def get_chat_config():
    """
    获取聊天配置
    
    返回系统支持的模型配置信息。
    """
    try:
        return {
            "models": MODEL_CONFIGS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

# 备忘录查询和删除接口

@router.get("/memos", response_model=List[Dict[str, Any]])
async def list_memos():
    """
    获取备忘录列表
    
    返回所有备忘录的列表。
    """
    try:
        memos = get_memo_messages()
        for memo in memos:
            try:
                memo['analysis'] = json.loads(memo['content'])
            except json.JSONDecodeError:
                memo['analysis'] = None
        return memos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备忘录列表失败: {str(e)}")

@router.get("/memos/{memo_id}", response_model=Dict[str, Any])
async def get_memo(memo_id: int):
    """
    获取备忘录详情
    
    返回指定备忘录的详细信息。
    """
    try:
        memo = get_memo_message(memo_id)
        if not memo:
            raise HTTPException(status_code=404, detail=f"备忘录不存在: {memo_id}")
        try:
            memo['analysis'] = json.loads(memo['content'])
        except json.JSONDecodeError:
            memo['analysis'] = None
        return memo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备忘录详情失败: {str(e)}")

@router.delete("/memos/{memo_id}", response_model=Dict[str, Any])
async def delete_memo(memo_id: int):
    """
    删除备忘录
    
    删除指定的备忘录。
    """
    try:
        deleted = delete_memo_message(memo_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"备忘录不存在: {memo_id}")
        return {
            "memo_id": memo_id,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除备忘录失败: {str(e)}")

@router.get("/memos/session/{session_id}", response_model=List[Dict[str, Any]])
async def list_memos_by_session(session_id: int):
    """
    获取指定会话的备忘录列表
    
    返回指定会话的所有备忘录。
    """
    try:
        memos = get_memo_messages_by_session(session_id)
        for memo in memos:
            try:
                memo['analysis'] = json.loads(memo['content'])
            except json.JSONDecodeError:
                memo['analysis'] = None
        return memos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话备忘录失败: {str(e)}")
