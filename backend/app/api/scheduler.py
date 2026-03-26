"""
任务调度API接口
提供任务管理和监控的API接口
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.scheduler import get_jobs, add_job, remove_job, pause_job, resume_job, capture_website_screenshot
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

@router.get("/jobs", response_model=List[Dict[str, Any]])
async def get_scheduled_jobs():
    """
    获取所有定时任务
    
    返回:
        list: 定时任务列表
    """
    try:
        jobs = get_jobs()
        job_list = []
        
        for job in jobs:
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger),
                "status": "paused" if job.next_run_time is None else "active"
            }
            job_list.append(job_info)
        
        return job_list
    except Exception as e:
        logger.error(f"获取定时任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取定时任务失败")

@router.post("/jobs")
async def add_scheduled_job(job_id: str, trigger: str, **kwargs):
    """
    添加定时任务
    
    参数:
        job_id: 任务ID
        trigger: 触发器类型 (interval, cron, date)
        **kwargs: 触发器参数
    
    返回:
        dict: 任务信息
    """
    try:
        # 这里可以根据需要添加不同类型的任务
        # 目前只支持网站截图任务
        if job_id == "capture_flk_screenshot":
            job = add_job(
                capture_website_screenshot,
                trigger,
                job_id,
                **kwargs
            )
            
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger),
                "status": "active"
            }
        else:
            raise HTTPException(status_code=400, detail="不支持的任务类型")
    except Exception as e:
        logger.error(f"添加定时任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="添加定时任务失败")

@router.delete("/jobs/{job_id}")
async def delete_scheduled_job(job_id: str):
    """
    删除定时任务
    
    参数:
        job_id: 任务ID
    
    返回:
        dict: 操作结果
    """
    try:
        remove_job(job_id)
        return {"success": True, "message": f"任务 {job_id} 已删除"}
    except Exception as e:
        logger.error(f"删除定时任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除定时任务失败")

@router.post("/jobs/{job_id}/pause")
async def pause_scheduled_job(job_id: str):
    """
    暂停定时任务
    
    参数:
        job_id: 任务ID
    
    返回:
        dict: 操作结果
    """
    try:
        pause_job(job_id)
        return {"success": True, "message": f"任务 {job_id} 已暂停"}
    except Exception as e:
        logger.error(f"暂停定时任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="暂停定时任务失败")

@router.post("/jobs/{job_id}/resume")
async def resume_scheduled_job(job_id: str):
    """
    恢复定时任务
    
    参数:
        job_id: 任务ID
    
    返回:
        dict: 操作结果
    """
    try:
        resume_job(job_id)
        return {"success": True, "message": f"任务 {job_id} 已恢复"}
    except Exception as e:
        logger.error(f"恢复定时任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="恢复定时任务失败")

@router.post("/jobs/{job_id}/run-now")
async def run_job_now(job_id: str):
    """
    立即执行定时任务
    
    参数:
        job_id: 任务ID
    
    返回:
        dict: 操作结果
    """
    try:
        from app.services.scheduler import scheduler
        
        job = scheduler.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"任务 {job_id} 不存在")
        
        # 立即执行任务
        job.modify(next_run_time=None)
        job.resume()
        scheduler.wakeup()
        
        return {"success": True, "message": f"任务 {job_id} 已触发执行"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"立即执行任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="立即执行任务失败")
