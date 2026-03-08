from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import random
import time
import jwt
import os
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

# 白名单手机号
WHITELIST_PHONE_NUMBERS = [
    "17800212735",
    "13800138000",
    "13900139000",
    "13700137000",
    "18310106903"
]

# 临时存储验证码 (手机号 -> (验证码, 过期时间))
verification_codes = {}

# JWT密钥
SECRET_KEY = os.getenv("SECRET_KEY", "p26j876xYHvYc4GzpX4E624NQc1vMf6c28ZvtxOvVvg")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic模型
class SendCodeRequest(BaseModel):
    phone: str

class LoginRequest(BaseModel):
    phone: str
    code: str

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
        raise HTTPException(
            status_code=401,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 全局身份校验依赖
def get_current_user(payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """获取当前用户信息"""
    return payload

@router.post("/send-code", response_model=Dict[str, Any])
async def send_verification_code(
    request: SendCodeRequest
):
    """
    发送验证码
    
    向指定手机号发送验证码，仅白名单中的手机号可使用。
    
    - **phone**: 手机号
    """
    # 检查是否在白名单中
    if request.phone not in WHITELIST_PHONE_NUMBERS:
        raise HTTPException(status_code=403, detail="该手机号不在白名单中")
    
    # 从手机号中间6位生成验证码
    code = request.phone[2:8]
    
    # 存储验证码，有效期5分钟
    expire_time = time.time() + 5 * 60
    verification_codes[request.phone] = (code, expire_time)
    
    # 模拟发送验证码
    print(f"向 {request.phone} 发送验证码: {code}")
    # 返回验证码以便测试
    print(f"验证码: {code}")
    
    return {
        "phone": request.phone,
        "message": "验证码已发送",
        "expire_in": 300  # 5分钟
    }

@router.post("/login", response_model=Dict[str, Any])
async def login(
    request: LoginRequest
):
    """
    登录
    
    使用手机号和验证码登录。
    
    - **phone**: 手机号
    - **code**: 验证码
    """
    # 检查是否在白名单中
    if request.phone not in WHITELIST_PHONE_NUMBERS:
        raise HTTPException(status_code=403, detail="该手机号不在白名单中")
    
    # 检查验证码
    if request.phone not in verification_codes:
        raise HTTPException(status_code=400, detail="验证码已过期或未发送")
    
    stored_code, expire_time = verification_codes[request.phone]
    if time.time() > expire_time:
        del verification_codes[request.phone]
        raise HTTPException(status_code=400, detail="验证码已过期")
    
    if request.code != stored_code:
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 验证码验证成功，删除验证码
    del verification_codes[request.phone]
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": request.phone})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "phone": request.phone,
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
    phone = payload.get("sub")
    if not phone:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    
    return {
        "phone": phone,
        "message": "获取用户信息成功"
    }
