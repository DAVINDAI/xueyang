"""
法律咨询API接口
提供法律法规相关的API接口，包括获取法律分类、文档列表、下载法律PDF文档等功能
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request, Body
from typing import List, Dict, Any
from app.services.law_scraper import law_scraper_service
from app.services.law_rag_service import law_rag_service
from app.exceptions import BusinessException, SystemException, ErrorCode
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/law", tags=["法律咨询"])

@router.post("/rag/query", response_model=Dict[str, Any])
async def law_rag_query(
    query: str = Body(..., description="查询文本"),
    model_name: str = Body("qwen-plus", description="模型名称"),
    top_k: int = Body(3, description="检索相关文档数量")
):
    """
    使用RAG技术回答法律问题
    
    参数:
        query: 查询文本
        model_name: 模型名称（可选，默认qwen-plus）
        top_k: 检索相关文档数量（可选，默认3）
        
    返回:
        dict: 包含答案和参考文档的结果
    """
    logger.info(f"收到法律RAG查询请求: {query}")
    
    try:
        result = law_rag_service.query_with_rag(query, model_name, top_k)
        logger.info("法律RAG查询完成")
        return result
    except Exception as e:
        logger.error(f"法律RAG查询失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"法律RAG查询失败: {str(e)}")

@router.post("/rag/search", response_model=List[Dict[str, Any]])
async def law_semantic_search(
    query: str = Body(..., description="查询文本"),
    top_k: int = Body(3, description="返回结果数量")
):
    """
    语义搜索法律文档
    
    参数:
        query: 查询文本
        top_k: 返回结果数量（可选，默认3）
        
    返回:
        list: 搜索结果列表
    """
    logger.info(f"收到法律文档语义搜索请求: {query}")
    
    try:
        results = law_rag_service.semantic_search(query, top_k)
        logger.info(f"语义搜索完成，找到 {len(results)} 个相关文档")
        return results
    except Exception as e:
        logger.error(f"语义搜索失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"语义搜索失败: {str(e)}")

@router.get("/rag/document-count", response_model=Dict[str, int])
async def get_law_document_count():
    """
    获取已索引的法律文档数量
    
    返回:
        dict: 包含文档数量的结果
    """
    logger.info("收到获取法律文档数量请求")
    
    try:
        count = law_rag_service.get_document_count()
        logger.info(f"已索引的法律文档数量: {count}")
        return {"count": count}
    except Exception as e:
        logger.error(f"获取法律文档数量失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"获取法律文档数量失败: {str(e)}")

@router.post("/rag/refresh-index")
async def refresh_law_index():
    """
    刷新法律文档索引
    
    返回:
        dict: 刷新结果信息
    """
    logger.info("收到刷新法律文档索引请求")
    
    try:
        result = law_rag_service.refresh_index()
        logger.info(result)
        return {"message": result}
    except Exception as e:
        logger.error(f"刷新法律文档索引失败: {str(e)}")
        raise SystemException(ErrorCode.SYSTEM_ERROR, f"刷新法律文档索引失败: {str(e)}")

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
