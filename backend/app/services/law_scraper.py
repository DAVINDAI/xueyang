"""
法律文档抓取服务
使用Playwright抓取国家法律法规数据库的法律文档
"""
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Playwright 为可选依赖，未安装时抓取功能不可用
try:
    from playwright.async_api import async_playwright
    _has_playwright = True
except ImportError:
    _has_playwright = False
    logger.warning("Playwright 未安装，法律法规抓取功能不可用")

# 确保下载目录存在
download_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "downloads"
)
os.makedirs(download_dir, exist_ok=True)

# 确保截图目录存在
screenshot_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "screenshots"
)
os.makedirs(screenshot_dir, exist_ok=True)


class LawScraperService:
    """
    法律文档抓取服务类
    """
    
    @property
    def law_data_dir(self):
        """
        获取法律文档存储目录
        
        返回:
            str: 法律文档存储目录路径
        """
        return download_dir
    
    def get_available_law_docs(self):
        """
        获取已下载的法律文档列表
        
        返回:
            list: 已下载的法律文档列表，包含文件名、文件路径、文件大小等信息
        """
        logger.info("获取已下载的法律文档列表")
        
        try:
            law_docs = []
            
            # 遍历下载目录下的所有文件
            for filename in os.listdir(download_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(download_dir, filename)
                    file_size = os.path.getsize(file_path)
                    
                    # 获取文件的修改时间（比创建时间更准确）
                    created_at = os.path.getmtime(file_path)
                    
                    # 确保文件大小和创建时间都是有效数值
                    if isinstance(file_size, int) and isinstance(created_at, float):
                        # 创建文档信息字典
                        doc_info = {
                            "filename": filename,
                            "file_path": file_path,
                            "file_size": file_size,
                            "created_at": created_at
                        }
                        
                        law_docs.append(doc_info)
                    else:
                        logger.warning(f"文件 {filename} 的属性无效，跳过")
            
            logger.info(f"找到 {len(law_docs)} 个已下载的法律文档")
            return law_docs
            
        except Exception as e:
            logger.error(f"获取已下载法律文档列表失败: {str(e)}")
            import traceback
            logger.error(f"堆栈追踪: {traceback.format_exc()}")
            return []
    
    async def fetch_law_documents(self):
        """
        使用Playwright获取国家法律法规数据库的法律文档
        """
        logger.info("开始执行法律法规获取任务")

        if not _has_playwright:
            logger.warning("法律法规获取任务跳过: Playwright 未安装")
            return

        try:
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
                            # 重命名文件到指定目录
                            import shutil
                            new_path = os.path.join(download_dir, download.suggested_filename)
                            # 如果文件已存在，跳过下载和处理
                            if os.path.exists(new_path):
                                logger.info(f"文件已存在: {new_path}，跳过下载和处理")
                                return
                            # 获取下载的文件路径
                            download_path = await download.path()
                            # 移动文件到指定位置
                            shutil.move(download_path, new_path)
                            logger.info(f"下载文件保存到: {new_path}")
                            
                            # 为PDF文件生成Markdown格式并与LlamaIndex集成
                            from app.services.pdf_processor import pdf_processor_service
                            if new_path.lower().endswith('.pdf'):
                                # 使用新实现的方法处理PDF文件，指定集合名称为法律文档的英文
                                result = pdf_processor_service.process_pdf_with_llamaindex(new_path, "law_documents")
                                if result:
                                    logger.info(result)
                                else:
                                    logger.warning("PDF处理失败")

                        new_page.on("download", handle_new_page_download)
                        
                        # 如果有 .right .tabs 公报原版 按钮 先点击该按钮
                        if await new_page.query_selector(".right .tabs:has-text(\"公报原版\")"):
                            logger.info("找到《公报原版》按钮，下载PDF文件")
                            # 点击公报原版按钮
                            await new_page.click(".right .tabs:has-text(\"公报原版\")")
                        else:
                            # 没有这个按钮，跳过下载
                            logger.warning("未找到《公报原版》按钮，跳过下载")
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
                
                logger.info(f"法律法规获取任务完成，截图保存路径: {screenshot_path}")
                
        except NotImplementedError:
            # 环境不支持 Playwright（如沙箱环境）
            logger.warning("法律法规获取任务失败: 当前环境不支持 Playwright 浏览器操作")
            logger.warning("这通常是由于沙箱环境限制或缺少必要的依赖导致的")
            logger.warning("任务将按照计划继续执行，但可能会在相同环境中失败")
        except Exception as e:
            logger.error(f"法律法规获取失败: {str(e)}")
            import traceback
            logger.error(f"堆栈追踪: {traceback.format_exc()}")

# 创建服务实例
law_scraper_service = LawScraperService()
