from fastapi import APIRouter, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import random
import time
import jwt
import os
from typing import Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
from app.exceptions import BusinessException, ValidationException, ErrorCode

# 加载环境变量
load_dotenv()

router = APIRouter()
security = HTTPBearer()

# 账号信息
USER_ACCOUNTS = [
    {"username": "president", "password": "president0", "role": "总裁"},
    {"username": "marketing", "password": "marketing0", "role": "市场"},
    {"username": "operation", "password": "operation0", "role": "运营"},
    {"username": "development", "password": "development0", "role": "研发"},
    {"username": "finance", "password": "finance0", "role": "财务"},
    {"username": "17800212735", "password": "178002127350", "role": "用户"}
]

# JWT密钥
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY环境变量未设置，请在启动脚本中设置或手动设置环境变量")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

# Pydantic模型
class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token(data: Dict[str, Any]) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的认证凭据"
        )

# 全局身份校验依赖
def get_current_user(payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """获取当前用户信息"""
    return payload

@router.post("/login", response_model=Dict[str, Any])
async def login(
    request: LoginRequest
):
    """
    登录
    
    使用用户名和密码登录。
    
    - **username**: 用户名
    - **password**: 密码
    """
    # 检查账号
    user = None
    for account in USER_ACCOUNTS:
        if account["username"] == request.username and account["password"] == request.password:
            user = account
            break
    
    if not user:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"],
        "message": "登录成功"
    }

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(
    payload: Dict[str, Any] = Depends(verify_token)
):
    """
    获取当前用户信息
    
    返回当前登录用户的信息。
    """
    username = payload.get("sub")
    role = payload.get("role")
    if not username:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的认证凭据"
        )
    
    return {
        "username": username,
        "role": role,
        "message": "获取用户信息成功"
    }
