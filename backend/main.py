from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import stats, details, chat, search, resume
from app.services.db import init_database, add_indexes_to_existing_db
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置时区为澳门时区（Asia/Macau，东8区）
os.environ['TZ'] = 'Asia/Macau'
import time
try:
    time.tzset()  # 应用时区设置
except AttributeError:
    pass  # Windows不支持tzset

# 创建FastAPI应用
app = FastAPI(
    title="LangGraph Chat API",
    description="大模型聊天和数据分析API",
    version="1.0.0",
    debug=True,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(details.router, prefix="/api/details", tags=["details"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(resume.router, prefix="/api", tags=["resume"])

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_database()
    add_indexes_to_existing_db()

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to LangGraph Chat API"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
