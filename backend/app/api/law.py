"""
法律咨询API接口
提供法律法规相关的API接口，包括获取法律分类、文档列表、下载法律PDF文档等功能
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Dict, Any
from app.services.law_scraper import law_scraper_service
from app.exceptions import BusinessException, SystemException, ErrorCode
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/law", tags=["法律咨询"])

@router.get("/documents", response_model=List[Dict[str, Any]])
async def get_available_law_docs():
    """
    获取已下载的法律文档列表
    
    返回:
        list: 已下载的法律文档列表，包含文件名、文件路径、文件大小等信息
    """
    logger.info("收到获取已下载法律文档列表的请求")
    
    try:
        law_docs = law_scraper_service.get_available_law_docs()
        logger.info(f"找到 {len(law_docs)} 个已下载的法律文档")
        return law_docs
    except Exception as e:
        logger.error(f"获取已下载法律文档列表失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "获取已下载法律文档失败")

@router.get("/download")
async def get_downloaded_pdf(
    filename: str = Query(..., description="法律文档文件名")
):
    """
    获取已下载的法律PDF文档
    
    参数:
        filename: 法律文档文件名
        
    返回:
        FileResponse: 法律PDF文档
    """
    logger.info(f"收到获取已下载法律PDF文档的请求，文件名: {filename}")
    
    try:
        from fastapi.responses import FileResponse
        
        law_docs = law_scraper_service.get_available_law_docs()
        
        for doc in law_docs:
            if doc["filename"] == filename:
                logger.info(f"返回法律PDF文档: {filename}")
                return FileResponse(
                    doc["file_path"],
                    filename=doc["filename"],
                    media_type="application/pdf"
                )
        
        logger.warning(f"未找到已下载的法律PDF文档: {filename}")
        raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "未找到法律PDF文档")
    
    except BusinessException as e:
        raise e
    except Exception as e:
        logger.error(f"获取已下载法律PDF文档失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "获取法律PDF文档失败")
