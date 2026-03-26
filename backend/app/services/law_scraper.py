"""
法律文档抓取服务
使用Playwright抓取国家法律法规数据库的法律文档
"""
import os
import logging
from datetime import datetime
from playwright.async_api import async_playwright

# 配置日志
logger = logging.getLogger(__name__)

# 确保下载目录存在
download_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "downloads"
)
os.makedirs(download_dir, exist_ok=True)


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
    
    async def fetch_law_links(self):
        """
        抓取国家法律法规数据库页面上的法律链接
        
        返回:
            list: 法律链接列表
        """
        logger.info("开始抓取法律链接")
        
        try:
            async with async_playwright() as p:
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
                
                # 抓取法律链接
                # 这里需要根据实际页面结构调整选择器
                law_links = []
                
                # 示例：抓取所有a标签中的链接
                links = await page.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if href and 'law' in href:
                        full_url = href if href.startswith('http') else f"https://flk.npc.gov.cn{href}"
                        law_links.append(full_url)
                
                # 关闭浏览器
                await browser.close()
                
                logger.info(f"成功抓取到 {len(law_links)} 个法律链接")
                return law_links
                
        except Exception as e:
            logger.error(f"抓取法律链接失败: {str(e)}")
            import traceback
            logger.error(f"堆栈追踪: {traceback.format_exc()}")
            return []
    
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
                    
                    # 创建文档信息字典
                    doc_info = {
                        "filename": filename,
                        "file_path": file_path,
                        "file_size": file_size,
                        "created_at": os.path.getctime(file_path)
                    }
                    
                    law_docs.append(doc_info)
            
            logger.info(f"找到 {len(law_docs)} 个已下载的法律文档")
            return law_docs
            
        except Exception as e:
            logger.error(f"获取已下载法律文档列表失败: {str(e)}")
            import traceback
            logger.error(f"堆栈追踪: {traceback.format_exc()}")
            return []
    
    async def fetch_law_categories(self):
        """
        获取法律法规分类列表
        
        返回:
            list: 法律法规分类列表，包含分类名称和链接
        """
        logger.info("获取法律法规分类列表")
        
        # 这里可以根据实际需求实现分类抓取逻辑
        # 暂时返回空列表
        return []
    
    async def fetch_law_documents(self, category_url):
        """
        获取特定分类下的法律文档列表
        
        参数:
            category_url: 法律法规分类页面URL
            
        返回:
            list: 法律文档列表，包含文档名称和链接
        """
        logger.info(f"获取分类下的法律文档列表: {category_url}")
        
        # 这里可以根据实际需求实现文档列表抓取逻辑
        # 暂时返回空列表
        return []
    
    async def download_law_pdf(self, law_url):
        """
        下载法律PDF文档
        
        参数:
            law_url: 法律文档链接
        
        返回:
            str: 下载的PDF文件路径
        """
        logger.info(f"开始下载法律PDF: {law_url}")
        
        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                # 创建页面
                page = await browser.new_page()
                
                # 设置下载目录
                await page.context.set_default_timeout(60000)
                
                # 访问法律文档页面
                await page.goto(law_url, 
                              wait_until='domcontentloaded', 
                              timeout=60000)
                
                # 等待页面加载
                await page.wait_for_timeout(2000)
                
                # 查找下载按钮并点击
                # 这里需要根据实际页面结构调整选择器
                try:
                    # 示例：查找下载按钮并点击
                    download_button = await page.query_selector('button:has-text("下载")')
                    if download_button:
                        # 点击下载按钮
                        await download_button.click()
                        
                        # 等待下载完成
                        async with page.expect_download() as download_info:
                            # 等待下载开始
                            download = await download_info.value
                            
                            # 生成下载文件名
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            file_name = f"law_{timestamp}.pdf"
                            download_path = os.path.join(download_dir, file_name)
                            
                            # 保存下载的文件
                            await download.save_as(download_path)
                            
                            logger.info(f"法律PDF下载成功，保存路径: {download_path}")
                            return download_path
                    else:
                        logger.warning(f"未找到下载按钮: {law_url}")
                        return None
                        
                except Exception as e:
                    logger.error(f"点击下载按钮失败: {str(e)}")
                    return None
                finally:
                    # 关闭浏览器
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"下载法律PDF失败: {str(e)}")
            import traceback
            logger.error(f"堆栈追踪: {traceback.format_exc()}")
            return None


# 创建服务实例
law_scraper_service = LawScraperService()
