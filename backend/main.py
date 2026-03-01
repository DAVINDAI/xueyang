from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import stats, details, chat, search, resume, auth
from app.services.db import init_database, add_indexes_to_existing_db
import os
from dotenv import load_dotenv
import jwt

# 加载环境变量
load_dotenv()

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY环境变量未设置，请在启动脚本中设置或手动设置环境变量")
ALGORITHM = "HS256"

# 不需要身份校验的路径（精确匹配）
EXCLUDE_PATHS = [
    "/api/auth/send-code",
    "/api/auth/login",
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc"
]

# 允许前缀匹配的路径（这些路径下的所有子路径都不需要认证）
EXCLUDE_PREFIX_PATHS = [
    "/api/chat/memos"
]

# 身份校验中间件
async def auth_middleware(request: Request, call_next):
    # 检查是否在排除路径中
    path = request.url.path
    
    # 精确匹配
    if path in EXCLUDE_PATHS:
        response = await call_next(request)
        return response
    
    # 前缀匹配（仅对特定路径）
    for prefix_path in EXCLUDE_PREFIX_PATHS:
        if path == prefix_path or path.startswith(prefix_path + "/"):
            response = await call_next(request)
            return response
    
    # 获取Authorization头
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={"detail": "未提供有效的认证凭据"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 提取token
    token = auth_header.split(" ")[1]
    
    # 验证token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user = payload
    except jwt.PyJWTError:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content={"detail": "无效的认证凭据"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    response = await call_next(request)
    return response

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

# 添加身份校验中间件（在CORS之前）
app.middleware("http")(auth_middleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(details.router, prefix="/api/details", tags=["details"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(resume.router, prefix="/api", tags=["resume"])

# 配置CORS（必须在最后添加，确保最先处理请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
