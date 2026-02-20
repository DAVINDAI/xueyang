from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import asyncio
import sqlite3
import logging
from app.config import TAVILY_CONFIG
from app.services.db import search_chat_messages

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

def search_web_sync(search_query, tavily_api_key):
    """同步搜索网络内容"""
    from tavily import TavilyClient
    client = TavilyClient(api_key=tavily_api_key)
    return client.search(
        query=search_query,
        search_depth="basic",
        max_results=5
    )

@router.post("/search")
async def search(request: SearchRequest):
    """搜索接口 - 返回Tavily网络搜索结果和本地聊天记录搜索结果"""
    try:
        search_query = request.query
        if not search_query:
            raise HTTPException(status_code=400, detail="查询参数不能为空")
        
        # 1. 搜索本地聊天记录
        local_results = []
        try:
            chat_messages = search_chat_messages(search_query, limit=5)
            for msg in chat_messages:
                local_results.append({
                    "type": "local",
                    "title": f"{msg['session_name']} - {msg['role']}",
                    "content": msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'],
                    "sessionId": msg['session_id'],
                    "messageId": msg['id'],
                    "createdAt": msg['created_at']
                })
        except sqlite3.Error as e:
            logger.error(f"SQLite数据库错误: {str(e)}", exc_info=True)
        except KeyError as e:
            logger.error(f"数据格式错误，缺少字段: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"本地搜索发生未预期错误: {str(e)}", exc_info=True)
        
        # 2. 搜索网络内容（Tavily）- 使用线程池避免阻塞
        web_results = []
        try:
            tavily_api_key = os.getenv(TAVILY_CONFIG["api_key_env"])
            if tavily_api_key:
                # 在单独的线程中执行同步搜索
                search_results = await asyncio.to_thread(
                    search_web_sync,
                    search_query,
                    tavily_api_key
                )
                
                for result in search_results.get("results", []):
                    web_results.append({
                        "type": "web",
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", "")
                    })
        except ImportError:
            logger.warning("Tavily SDK未安装，跳过网络搜索")
        except KeyError as e:
            logger.error(f"Tavily API响应格式错误: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"网络搜索失败: {str(e)}", exc_info=True)
        
        # 3. 合并结果，本地结果在前
        all_results = local_results + web_results
        
        return {"results": all_results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
