from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.autogen_service import autogen_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/evolution", response_model=Dict[str, Any])
async def evolve_website():
    """
    执行网站进化
    
    触发 AutoGen 服务，生成网站优化建议
    """
    try:
        logger.info("开始执行网站进化...")
        
        # 调用 AutoGen 服务生成进化建议
        suggestions = autogen_service.generate_evolution_suggestions()
        
        if "error" in suggestions:
            raise HTTPException(status_code=500, detail=suggestions["error"])
        
        logger.info("网站进化执行完成")
        return {
            "status": "success",
            "data": suggestions
        }
        
    except Exception as e:
        logger.error(f"执行网站进化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行网站进化失败: {str(e)}")
