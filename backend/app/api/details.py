from fastapi import APIRouter, HTTPException, Query
from app.services.db import get_session_details
from typing import Dict, Any, List

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_all_details():
    """
    获取所有详情信息
    
    返回所有会话的简要信息，包括会话ID、名称、模型、创建时间和消息数量等。
    """
    try:
        details = get_session_details()
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详情信息失败: {str(e)}")

@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_session_details_api(session_id: int):
    """
    获取会话详情
    
    返回指定会话的详细信息，包括会话信息和消息历史。
    
    - **session_id**: 会话ID
    """
    try:
        details = get_session_details(session_id)
        if not details.get("session"):
            raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话详情失败: {str(e)}")

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def get_sessions_list():
    """
    获取会话列表
    
    返回所有会话的简要信息列表。
    """
    try:
        details = get_session_details()
        return details.get("sessions", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")
