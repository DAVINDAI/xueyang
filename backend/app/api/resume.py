from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.pdf_processor import PDFProcessor
from app.services.resume_optimizer import ResumeOptimizer
import os

router = APIRouter(prefix="/resume", tags=["resume"])

# 初始化服务
pdf_processor = PDFProcessor()
resume_optimizer = ResumeOptimizer()

@router.post("/optimize")
async def optimize_resume(
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
        return {"data": result}
        
    except Exception as e:
        print(f"简历优化失败: {e}")
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
