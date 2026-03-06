from fastapi import APIRouter, HTTPException
from app.services.db import get_stats
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_statistics():
    """
    获取统计信息
    
    返回系统的统计数据，包括会话数量、消息数量、模型使用统计和每日消息统计等。
    """
    try:
        stats = get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.get("/models", response_model=Dict[str, Any])
async def get_model_stats():
    """
    获取模型使用统计
    
    返回不同模型的使用情况统计。
    """
    try:
        stats = get_stats()
        return {
            "model_stats": stats.get("model_stats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型统计信息失败: {str(e)}")

@router.get("/daily", response_model=Dict[str, Any])
async def get_daily_stats():
    """
    获取每日消息统计
    
    返回最近7天的消息数量统计。
    """
    try:
        stats = get_stats()
        return {
            "daily_stats": stats.get("daily_stats", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日统计信息失败: {str(e)}")
