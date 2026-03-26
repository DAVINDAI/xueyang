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


async def capture_website_screenshot():
    """
    使用Playwright访问国家法律法规数据库并截图
    """
    logger.info("开始执行网站截图任务")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 确保下载目录存在
            download_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "downloads"
            )
            os.makedirs(download_dir, exist_ok=True)
            
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # 创建页面
            page = await browser.new_page()
            
            # 访问网站
            await page.goto("https://flk.npc.gov.cn/index", 
                          wait_until='domcontentloaded', 
                          timeout=60000)
            
            # 等待页面加载
            await page.wait_for_timeout(2000)
            
            # 生成截图文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"flk_{timestamp}.png")
            
            # 截图
            await page.screenshot(
                path=screenshot_path,
                full_page=True
            )

            # 找到页面上list-title 的所有元素
            list_titles = await page.query_selector_all(".list-title")
            for title in list_titles:
                title_text = await title.text_content()
                logger.info(f"找到标题: {title_text}")
                # 这里可以添加将标题保存到数据库的逻辑
                # 例如：await save_to_db(title_text)
                # 检查元素是否可见
                is_visible = await title.is_visible()
                if not is_visible:
                    logger.warning(f"标题 '{title_text}' 不可见，跳过")
                    continue
                # 滚动到元素位置，确保元素可见
                await title.scroll_into_view_if_needed()
                # 点击标题
                await title.click()
                # 等待新的页面打开
                await page.wait_for_timeout(2000)
                # 获取所有打开的页面
                pages = page.context.pages
                # 切换到最新的页面（新打开的页面）
                if len(pages) > 1:
                    new_page = pages[-1]
                    # 等待页面加载
                    await new_page.wait_for_load_state('domcontentloaded')
                    
                    # 在新页面上也注册下载事件处理器
                    async def handle_new_page_download(download):
                        # 获取下载的文件路径
                        download_path = await download.path()
                        # 重命名文件到指定目录
                        import shutil
                        new_path = os.path.join(download_dir, download.suggested_filename)
                        # 如果文件已存在，先删除
                        if os.path.exists(new_path):
                            logger.warning(f"文件已存在: {new_path}，删除旧文件")
                            os.remove(new_path)
                        shutil.move(download_path, new_path)
                        logger.info(f"下载文件保存到: {new_path}")
                        
                        # 为PDF文件生成Markdown格式
                        from app.services.document_hasher import document_converter_service
                        if new_path.lower().endswith('.pdf'):
                            markdown_content = document_converter_service.pdf_to_markdown(new_path)
                            if markdown_content:
                                # 保存Markdown文件
                                markdown_path = os.path.splitext(new_path)[0] + '.md'
                                with open(markdown_path, 'w', encoding='utf-8') as f:
                                    f.write(markdown_content)
                                logger.info(f"PDF转换为Markdown并保存到: {markdown_path}")

                    new_page.on("download", handle_new_page_download)
                    
                    # 如果有 .right .tabs 公报原版 按钮 先点击该按钮
                    if await new_page.query_selector(".right .tabs:has-text(\"公报原版\")"):
                        logger.info("找到公报原版按钮，下载PDF文件")
                        # 点击公报原版按钮
                        await new_page.click(".right .tabs:has-text(\"公报原版\")")
                    else:
                        # 没有这个按钮，跳过下载
                        logger.warning("未找到公报原版按钮，跳过下载")
                        continue


                    # 鼠标hover到download 按钮
                    await new_page.hover(".download")
                    # 等待页面加载
                    await new_page.wait_for_timeout(1000)
                    
                    # 截图
                    await new_page.screenshot(
                        path=os.path.join(screenshot_dir, f"flk_{timestamp}_{title_text.replace(' ', '_')}.png"),
                        full_page=True
                    )

                    # 检查click-download元素是否可见
                    click_download = await new_page.query_selector(".click-download")
                    if click_download:
                        is_visible = await click_download.is_visible()
                        if is_visible:
                            # 点击click-download 按钮 这里会触发下载文档的动作 保存下载的文档到默认下载目录
                            await new_page.click(".click-download")
                            # 等待页面加载
                            await new_page.wait_for_timeout(5000)
                        else:
                            logger.warning("下载按钮不可见，跳过下载")
                    else:
                        logger.warning("未找到下载按钮，跳过下载")

                    # 关闭新页面
                    await new_page.close()
            
            # 关闭浏览器
            await browser.close()
            
            logger.info(f"网站截图成功，保存路径: {screenshot_path}")
            
    except NotImplementedError:
        # 环境不支持 Playwright（如沙箱环境）
        logger.warning("网站截图任务失败: 当前环境不支持 Playwright 浏览器操作")
        logger.warning("这通常是由于沙箱环境限制或缺少必要的依赖导致的")
        logger.warning("任务将按照计划继续执行，但可能会在相同环境中失败")
    except Exception as e:
        logger.error(f"网站截图失败: {str(e)}")
        import traceback
        logger.error(f"堆栈追踪: {traceback.format_exc()}")


async def run_scheduled_screenshot_task():
    """
    运行网站截图任务并捕获所有异常
    """
    try:
        await capture_website_screenshot()
    except Exception as e:
        # 捕获所有异常，防止 asyncio 记录未处理的异常
        logger.error(f"执行网站截图任务时发生异常: {str(e)}")
        import traceback
        logger.error(f"堆栈追踪: {traceback.format_exc()}")


def start_scheduler():
    """
    启动调度器并添加任务
    """
    logger.info("正在启动调度器...")
    
    # 添加网站截图任务
    # 每小时执行一次
    scheduler.add_job(
        run_scheduled_screenshot_task,
        'interval',
        hours=1,
        id='capture_flk_screenshot',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("调度器启动成功")
    
    # 启动时自动执行一次网站截图任务
    logger.info("启动时自动执行网站截图任务...")
    try:
        # 使用 asyncio.create_task() 在现有事件循环中执行异步任务
        import asyncio
        asyncio.create_task(run_scheduled_screenshot_task())
    except Exception as e:
        logger.error(f"启动时执行网站截图任务失败: {str(e)}")
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
