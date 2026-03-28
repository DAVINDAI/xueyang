"""
定时任务调度服务
使用APScheduler实现定时任务调度，支持任务的添加、删除、暂停和恢复
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logging
import os
import asyncio
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置调度器
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')  # 使用SQLite存储任务
}
executors = {
    'default': ThreadPoolExecutor(10)  # 线程池执行器
}
job_defaults = {
    'coalesce': False,  # 任务堆积时是否合并
    'max_instances': 1  # 最大实例数
}

# 初始化调度器
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults
)

# 确保截图目录存在
screenshot_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "screenshots"
)
os.makedirs(screenshot_dir, exist_ok=True)


from app.services.law_scraper import law_scraper_service


async def run_scheduled_law_fetch_task():
    """
    运行法律法规获取任务并捕获所有异常
    """
    try:
        await law_scraper_service.fetch_law_documents()
    except Exception as e:
        # 捕获所有异常，防止 asyncio 记录未处理的异常
        logger.error(f"执行法律法规获取任务时发生异常: {str(e)}")
        import traceback
        logger.error(f"堆栈追踪: {traceback.format_exc()}")


def start_scheduler():
    """
    启动调度器并添加任务
    """
    logger.info("正在启动调度器...")
    
    # 添加法律法规获取任务
    # 每小时执行一次
    scheduler.add_job(
        run_scheduled_law_fetch_task,
        'interval',
        hours=1,
        id='fetch_law_documents',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("调度器启动成功")
    
    # 启动时自动执行一次法律法规获取任务
    logger.info("启动时自动执行法律法规获取任务...")
    try:
        # 使用 asyncio.create_task() 在现有事件循环中执行异步任务
        import asyncio
        asyncio.create_task(run_scheduled_law_fetch_task())
    except Exception as e:
        logger.error(f"启动时执行法律法规获取任务失败: {str(e)}")
        import traceback
        logger.error(f"堆栈追踪: {traceback.format_exc()}")


def stop_scheduler():
    """
    停止调度器
    """
    logger.info("正在关闭调度器...")
    scheduler.shutdown()
    logger.info("调度器已关闭")


def get_jobs():
    """
    获取所有任务
    """
    return scheduler.get_jobs()


def add_job(func, trigger, id, **kwargs):
    """
    添加任务
    """
    return scheduler.add_job(func, trigger, id=id, replace_existing=True, **kwargs)


def remove_job(job_id):
    """
    删除任务
    """
    scheduler.remove_job(job_id)


def pause_job(job_id):
    """
    暂停任务
    """
    job = scheduler.get_job(job_id)
    if job:
        job.pause()


def resume_job(job_id):
    """
    恢复任务
    """
    job = scheduler.get_job(job_id)
    if job:
        job.resume()
