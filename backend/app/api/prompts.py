from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging

from app.services.prompt_manager import prompt_manager_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["提示词管理"])


class UploadPromptRequest(BaseModel):
    name: str
    content: str
    description: Optional[str] = None


class BatchUploadRequest(BaseModel):
    prompts: Dict[str, Dict[str, str]]


@router.post("/upload")
async def upload_prompt(request: UploadPromptRequest):
    """
    上传单个提示词到 LangSmith
    """
    try:
        success = prompt_manager_service.upload_prompt(
            prompt_name=request.name,
            prompt_content=request.content,
            description=request.description
        )
        
        if success:
            return {
                "success": True,
                "message": f"提示词 '{request.name}' 上传成功"
            }
        else:
            raise HTTPException(status_code=500, detail="上传提示词失败")
            
    except Exception as e:
        logger.error(f"上传提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-upload")
async def batch_upload_prompts(request: BatchUploadRequest):
    """
    批量上传提示词到 LangSmith
    """
    try:
        results = prompt_manager_service.upload_prompts(request.prompts)
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        return {
            "success": True,
            "message": f"批量上传完成: {success_count}/{total_count} 成功",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量上传提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-default")
async def initialize_default_prompts():
    """
    初始化默认提示词到 LangSmith
    """
    try:
        success = prompt_manager_service.initialize_default_prompts()
        
        if success:
            return {
                "success": True,
                "message": "默认提示词初始化成功"
            }
        else:
            return {
                "success": False,
                "message": "部分提示词初始化失败，请查看日志"
            }
            
    except Exception as e:
        logger.error(f"初始化默认提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_prompts():
    """
    列出 LangSmith 中的所有提示词
    """
    try:
        prompts = prompt_manager_service.client.list_prompts()
        
        prompt_list = []
        for prompt in prompts:
            versions = prompt_manager_service.client.list_prompt_versions(prompt.id)
            latest_version = versions[0] if versions else None
            
            prompt_list.append({
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
                "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
                "latest_version": {
                    "id": latest_version.id,
                    "created_at": latest_version.created_at.isoformat() if latest_version.created_at else None
                } if latest_version else None
            })
        
        return {
            "success": True,
            "prompts": prompt_list
        }
        
    except Exception as e:
        logger.error(f"列出提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{prompt_name}")
async def get_prompt(prompt_name: str):
    """
    获取指定提示词的内容
    """
    try:
        content = prompt_manager_service.get_prompt(prompt_name)
        
        if content:
            return {
                "success": True,
                "name": prompt_name,
                "content": content
            }
        else:
            raise HTTPException(status_code=404, detail=f"提示词 '{prompt_name}' 不存在")
            
    except Exception as e:
        logger.error(f"获取提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh/{prompt_name}")
async def refresh_prompt(prompt_name: str):
    """
    刷新指定提示词（从 LangSmith 重新获取）
    """
    try:
        content = prompt_manager_service.refresh_prompt(prompt_name)
        
        if content:
            return {
                "success": True,
                "message": f"提示词 '{prompt_name}' 刷新成功",
                "content": content
            }
        else:
            raise HTTPException(status_code=404, detail=f"提示词 '{prompt_name}' 不存在")
            
    except Exception as e:
        logger.error(f"刷新提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache():
    """
    清除本地提示词缓存
    """
    try:
        prompt_manager_service.clear_cache()
        
        return {
            "success": True,
            "message": "缓存已清除"
        }
        
    except Exception as e:
        logger.error(f"清除缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
