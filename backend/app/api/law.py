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

@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_law_categories():
    """
    获取法律法规分类列表
    
    返回:
        list: 法律法规分类列表，包含分类名称和链接
    """
    logger.info("收到获取法律法规分类列表的请求")
    
    try:
        categories = await law_scraper_service.fetch_law_categories()
        return categories
    except Exception as e:
        logger.error(f"获取法律法规分类列表失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "获取法律法规分类失败")

@router.get("/documents", response_model=List[Dict[str, Any]])
async def get_law_documents(
    category_url: str = Query(..., description="法律法规分类页面URL")
):
    """
    获取特定分类下的法律文档列表
    
    参数:
        category_url: 法律法规分类页面URL
        
    返回:
        list: 法律文档列表，包含文档名称和链接
    """
    logger.info(f"收到获取法律文档列表的请求，分类URL: {category_url}")
    
    try:
        documents = await law_scraper_service.fetch_law_documents(category_url)
        return documents
    except Exception as e:
        logger.error(f"获取法律文档列表失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "获取法律文档失败")

@router.get("/download")
async def download_law_document(
    law_url: str = Query(..., description="法律文档页面URL"),
    request: Request = None
):
    """
    下载法律PDF文档
    
    参数:
        law_url: 法律文档页面URL
        
    返回:
        dict: 下载结果，包含文件路径和状态信息
    """
    logger.info(f"收到下载法律文档的请求，文档URL: {law_url}")
    
    try:
        # 检查是否有访问权限（可选，根据实际需求）
        visitor_id = getattr(request.state, 'visitor_id', None)
        if visitor_id:
            logger.info(f"访客ID: {visitor_id} 正在下载法律文档")
        
        # 下载法律文档
        pdf_path = await law_scraper_service.download_law_pdf(law_url)
        
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"法律文档下载成功: {pdf_path}")
            
            return {
                "success": True,
                "filename": os.path.basename(pdf_path),
                "file_path": pdf_path,
                "file_size": os.path.getsize(pdf_path),
                "message": "法律文档下载成功"
            }
        else:
            logger.warning(f"未找到或无法下载法律文档: {law_url}")
            raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "未找到法律文档")
    
    except BusinessException as e:
        raise e
    except Exception as e:
        logger.error(f"下载法律文档失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "下载法律文档失败")

@router.get("/available-docs", response_model=List[Dict[str, Any]])
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

@router.get("/document-info")
async def get_law_document_info(
    filename: str = Query(..., description="法律文档文件名")
):
    """
    获取法律文档的详细信息
    
    参数:
        filename: 法律文档文件名
        
    返回:
        dict: 法律文档详细信息
    """
    logger.info(f"收到获取法律文档信息的请求，文件名: {filename}")
    
    try:
        law_docs = law_scraper_service.get_available_law_docs()
        
        for doc in law_docs:
            if doc["filename"] == filename:
                logger.info(f"找到法律文档信息: {filename}")
                return doc
        
        logger.warning(f"未找到法律文档信息: {filename}")
        raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "未找到法律文档信息")
    
    except BusinessException as e:
        raise e
    except Exception as e:
        logger.error(f"获取法律文档信息失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "获取法律文档信息失败")

@router.get("/downloaded-pdf")
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

@router.get("/cleanup")
async def cleanup_law_docs():
    """
    清理法律文档存储目录
    
    注意: 此操作会删除所有已下载的法律文档，请谨慎使用
    
    返回:
        dict: 清理结果
    """
    logger.warning("收到清理法律文档存储目录的请求")
    
    try:
        law_data_dir = law_scraper_service.law_data_dir
        
        # 删除所有PDF文件
        deleted_files = []
        for filename in os.listdir(law_data_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(law_data_dir, filename)
                os.remove(file_path)
                deleted_files.append(filename)
        
        logger.info(f"成功删除 {len(deleted_files)} 个法律文档")
        return {
            "success": True,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "message": f"成功删除 {len(deleted_files)} 个法律文档"
        }
    except Exception as e:
        logger.error(f"清理法律文档存储目录失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, "清理法律文档存储目录失败")
