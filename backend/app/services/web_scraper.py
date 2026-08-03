import asyncio
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

# Playwright 为可选依赖，未安装时抓取功能不可用
try:
    from playwright.async_api import async_playwright
    _has_playwright = True
except ImportError:
    _has_playwright = False
    logger.warning("Playwright 未安装，网页抓取功能不可用")


class WebScraper:
    def __init__(self):
        self.cookie_file = os.path.join(os.path.dirname(__file__), '..', '..', 'cookies.json')
        self.browser_context_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'browser_context')
        os.makedirs(self.browser_context_dir, exist_ok=True)

    def is_url(self, text):
        """判断是否为URL"""
        url_pattern = re.compile(
            r'^(https?://)?'
            r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'
            r'(/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$'
        )
        return bool(url_pattern.match(text.strip()))

    async def fetch_job_description(self, url):
        """
        抓取职位描述（需要 Playwright）
        """
        if not _has_playwright:
            return ""

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=False,
                        args=['--disable-blink-features=AutomationControlled']
                    )

                    context = await browser.new_context(
                        storage_state=os.path.join(self.browser_context_dir, 'state.json') if os.path.exists(os.path.join(self.browser_context_dir, 'state.json')) else None
                    )

                    page = await context.new_page()

                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=60000)

                        try:
                            await page.screenshot(path=os.path.join(os.path.dirname(__file__), '..', '..', 'debug_screenshot.png'))
                            print("截图已保存: debug_screenshot.png")
                        except:
                            print("截图失败，继续执行")

                        await self._handle_login(page)
                        await asyncio.sleep(2)

                        job_description = await self._extract_job_content(page)

                        await context.storage_state(path=os.path.join(self.browser_context_dir, 'state.json'))
                        print("浏览器状态已保存")

                        return job_description

                    finally:
                        await browser.close()
            except Exception as e:
                retry_count += 1
                print(f"抓取失败，正在重试 ({retry_count}/{max_retries}): {str(e)}")
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                else:
                    print("达到最大重试次数，抓取失败")
                    return ""

    async def _handle_login(self, page):
        state_file = os.path.join(self.browser_context_dir, 'state.json')
        if not os.path.exists(state_file):
            print("首次运行，请在浏览器中完成登录")
            print("登录完成后，程序会自动继续...")
            await asyncio.sleep(45)
            print("继续执行")

    async def _extract_job_content(self, page):
        content_selectors = [
            '.job-sec', '.job-detail-content', '.position-content',
            '.zp-job-detail', '[class*="zp-job-desc"]', '.job-description',
            '.job-desc', '.position-desc', '.job-detail', '.position-detail',
            'article', 'main'
        ]
        for selector in content_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if len(text.strip()) > 50:
                        return text.strip()
            except:
                continue
        try:
            body_text = await page.inner_text('body')
            return self._clean_content(body_text)
        except:
            return ""

    def _clean_content(self, text):
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)

    def _load_cookies(self):
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载cookies失败: {e}")
        return None

    async def _save_cookies(self, context):
        try:
            cookies = await context.cookies()
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("Cookies已保存")
        except Exception as e:
            print(f"保存cookies失败: {e}")


web_scraper_service = WebScraper()
