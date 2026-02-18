from fastapi import APIRouter, HTTPException
import os
from app.config import TAVILY_CONFIG

router = APIRouter()

@router.post("/search")
async def search(query: dict):
    """搜索接口"""
    try:
        from tavily import TavilyClient
        
        # 获取查询参数
        search_query = query.get("query", "")
        if not search_query:
            raise HTTPException(status_code=400, detail="查询参数不能为空")
        
        # 获取Tavily API密钥
        tavily_api_key = os.getenv(TAVILY_CONFIG["api_key_env"])
        if not tavily_api_key:
            raise HTTPException(status_code=500, detail="Tavily API密钥未配置")
        
        # 创建Tavily客户端
        client = TavilyClient(api_key=tavily_api_key)
        
        # 调用Tavily API
        search_results = client.search(
            query=search_query,
            search_depth="basic",
            max_results=5
        )
        
        # 处理搜索结果
        results = []
        for result in search_results.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            })
        
        return {"results": results}
        
    except ImportError:
        raise HTTPException(status_code=500, detail="Tavily Python SDK未安装，请运行: pip install tavily-python")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
