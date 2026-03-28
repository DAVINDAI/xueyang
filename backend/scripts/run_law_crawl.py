#!/usr/bin/env python3
"""
执行法律法规抓取任务的脚本
用于手动运行 crawl_law_documents 函数
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.law_scraper import law_scraper_service

async def main():
    """
    主函数，执行法律法规抓取任务
    """
    print("开始执行法律法规抓取任务...")
    try:
        await law_scraper_service.fetch_law_documents()
        print("法律法规抓取任务执行完成！")
    except Exception as e:
        print(f"执行任务时发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
