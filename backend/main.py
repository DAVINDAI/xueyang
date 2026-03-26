from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import stats, details, chat, search, resume, auth, notes, coding_playground, evolution
from app.services.db import init_database, add_indexes_to_existing_db
from app.services.visitor_manager import visitor_manager
from app.exceptions import BaseException as CustomBaseException, BusinessException, SystemException, ValidationException, ErrorCode
import os
import uuid
from dotenv import load_dotenv
import jwt
import logging
import traceback

# 配置日志
logger = logging.getLogger(__name__)

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
EXCLUDE_PREFIX_PATHS = []

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
    
    # 如果有Bearer token，验证token并设置visitor_id为phone
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        # 验证token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = payload
            # 为登录用户设置visitor_id为手机号
            phone = payload.get("sub")
            if phone:
                request.state.visitor_id = phone
                logger.info(f"为登录用户设置visitor_id为手机号: {phone}")
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "认证凭据已过期"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"detail": "无效的认证凭据"})
        except Exception as e:
            logger.error(f"JWT验证异常: {e}")
            return JSONResponse(status_code=401, content={"detail": "认证失败"})
    else:
        # 没有token，生成临时visitor_id
        visitor_id = request.headers.get("X-Visitor-ID")
        if visitor_id:
            request.state.visitor_id = visitor_id
            logger.info(f"从请求头获取访客ID: {visitor_id}")
        else:
            request.state.visitor_id = f"temp_{uuid.uuid4()}"
            logger.info(f"生成临时访客ID: {request.state.visitor_id}")
    
    # 更新访客最后访问时间
    if hasattr(request.state, "visitor_id") and request.state.visitor_id:
        try:
            visitor_manager.update_visitor(request.state.visitor_id)
        except Exception as e:
            logger.error(f"更新访客信息失败: {e}")
    
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
    title="学氧助手API",
    description="大模型聊天和数据分析API",
    version="1.0.0",
    debug=True,
)

# 添加身份校验中间件（在CORS之后）
app.middleware("http")(auth_middleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(details.router, prefix="/api/details", tags=["details"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(coding_playground.router, prefix="/api", tags=["coding_playground"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(evolution.router, prefix="/api", tags=["evolution"])

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

# 统一异常处理中间件
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 生成请求唯一标识
    request_id = str(uuid.uuid4())
    
    # 记录完整的堆栈信息
    logger.error(f"请求ID: {request_id}")
    logger.error(f"请求路径: {request.url}")
    logger.error(f"异常类型: {type(exc).__name__}")
    logger.error(f"异常消息: {str(exc)}")
    logger.error(f"堆栈信息:\n{traceback.format_exc()}")
    
    # 根据异常类型返回不同的响应
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code * 100 + 1,
                "message": exc.detail,
                "error_type": "http_error",
                "request_id": request_id
            }
        )
    elif isinstance(exc, CustomBaseException):
        return JSONResponse(
            status_code=400 if exc.error_type == "business_error" or exc.error_type == "validation_error" else 500,
            content={
                "code": exc.code,
                "message": exc.message,
                "error_type": exc.error_type,
                "request_id": request_id,
                **exc.kwargs
            }
        )
    else:
        # 系统错误
        return JSONResponse(
            status_code=400,  # 不返回500，统一返回400或其他自定义状态码
            content={
                "code": ErrorCode.SYSTEM_ERROR,
                "message": "系统服务暂时不可用，请稍后重试",
                "error_type": "system_error",
                "request_id": request_id
            }
        )

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to 学氧助手API"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
