from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from app.services.pdf_processor import PDFProcessor
from app.services.resume_optimizer import ResumeOptimizer
from app.services.db import get_resume_optimizations, get_resume_optimization, delete_resume_optimization, save_resume_optimization
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])

# 初始化服务
pdf_processor = PDFProcessor()
resume_optimizer = ResumeOptimizer()

@router.post("/optimize")
async def optimize_resume(
    request: Request,
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    优化简历
    
    Args:
        resume: PDF格式的简历文件
        job_description: 职位描述
        
    Returns:
        dict: 包含优化结果的字典
    """
    # 验证文件类型
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持PDF格式文件")
    
    # 验证文件大小（10MB）
    file_size = 0
    file_content = b''
    while chunk := await resume.read(1024 * 1024):  # 1MB chunks
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        file_content += chunk
    
    # 验证文件内容
    if not file_content:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    # 验证是否为有效的PDF文件
    if not pdf_processor.validate_pdf(file_content):
        raise HTTPException(status_code=400, detail="无效的PDF文件")
    
    # 提取PDF文本内容
    resume_text = pdf_processor.extract_text(file_content)
    if not resume_text:
        raise HTTPException(status_code=400, detail="无法从PDF文件中提取文本内容")
    
    # 验证职位描述
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="职位描述不能为空")
    
    try:
        # 优化简历
        result = resume_optimizer.optimize_resume(resume_text, job_description)
        
        # 保存优化结果到数据库
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        save_resume_optimization(
            visitor_id=visitor_id,
            job_title=result.get("job_title", ""),
            job_description=job_description,
            industry_analysis=result.get("industry_analysis", ""),
            optimized_resume=result.get("optimized_resume", ""),
            optimization_suggestions=result.get("optimization_suggestions", []),
            matching_analysis=result.get("matching_analysis", {}),
            interview_preparation=result.get("interview_preparation", "")
        )
        
        return {"data": result}
        
    except Exception as e:
        logger.error(f"简历优化失败: {e}")
        raise HTTPException(status_code=500, detail="简历优化失败，请稍后重试")

@router.get("/download/{resume_id}")
async def download_resume(resume_id: str):
    """
    下载优化后的简历
    
    Args:
        resume_id: 简历ID
        
    Returns:
        FileResponse: 优化后的简历文件
    """
    # 实现下载逻辑
    # 注意：这里需要根据实际存储方式实现
    raise HTTPException(status_code=501, detail="下载功能开发中")

@router.get("/optimizations")
async def get_resume_optimization_list(request: Request, limit: int = 100):
    """
    获取所有简历优化结果
    
    Args:
        limit: 结果数量限制
        
    Returns:
        List[Dict]: 优化结果列表
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        optimizations = get_resume_optimizations(visitor_id, limit=limit)
        return {"data": optimizations}
    except Exception as e:
        logger.error(f"获取优化结果列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取优化结果列表失败")

@router.get("/optimizations/{optimization_id}")
async def get_single_resume_optimization(request: Request, optimization_id: int):
    """
    获取单个简历优化结果
    
    Args:
        optimization_id: 优化结果ID
        
    Returns:
        Dict: 优化结果
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        optimization = get_resume_optimization(visitor_id, optimization_id)
        if not optimization:
            raise HTTPException(status_code=404, detail="优化结果不存在")
        return {"data": optimization}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取优化结果失败: {e}")
        raise HTTPException(status_code=500, detail="获取优化结果失败")

@router.delete("/optimizations/{optimization_id}")
async def delete_single_resume_optimization(request: Request, optimization_id: int):
    """
    删除简历优化结果
    
    Args:
        optimization_id: 优化结果ID
        
    Returns:
        Dict: 删除结果
    """
    try:
        # 当state属性不存在时，visitor_id取空值
        visitor_id = getattr(request.state, 'visitor_id', None)
        deleted = delete_resume_optimization(visitor_id, optimization_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="优化结果不存在")
        return {"success": True, "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除优化结果失败: {e}")
        raise HTTPException(status_code=500, detail="删除优化结果失败")
