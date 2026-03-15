from fastapi import APIRouter, HTTPException, Request
from app.services.db import get_stats
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_statistics(request: Request):
    """
    获取统计信息
    
    返回系统的统计数据，包括会话数量、消息数量、模型使用统计和每日消息统计等。
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        stats = get_stats(visitor_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/models", response_model=Dict[str, Any])
async def get_model_stats(request: Request):
    """
    获取模型使用统计
    
    返回不同模型的使用情况统计。
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        stats = get_stats(visitor_id)
        return {
            "model_stats": stats.get("model_stats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型统计信息失败: {str(e)}")

@router.get("/daily", response_model=Dict[str, Any])
async def get_daily_stats(request: Request):
    """
    获取每日消息统计
    
    返回最近7天的消息数量统计。
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        stats = get_stats(visitor_id)
        return {
            "daily_stats": stats.get("daily_stats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日统计信息失败: {str(e)}")
