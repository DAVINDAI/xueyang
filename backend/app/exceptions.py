"""
自定义异常类定义
"""


class CustomException(Exception):
    """
    基础异常类，所有自定义异常都应继承此类
    """
    def __init__(self, code: int, message: str, error_type: str = "system_error", **kwargs):
        self.code = code
        self.message = message
        self.error_type = error_type
        self.kwargs = kwargs
        super().__init__(message)


class BusinessException(CustomException):
    """
    业务异常类，用于处理业务逻辑错误
    """
    def __init__(self, code: int, message: str, error_type: str = "business_error", **kwargs):
        super().__init__(code, message, error_type, **kwargs)


class SystemException(CustomException):
    """
    系统异常类，用于处理系统级错误
    """
    def __init__(self, code: int, message: str, error_type: str = "system_error", **kwargs):
        super().__init__(code, message, error_type, **kwargs)


class ValidationException(CustomException):
    """
    验证异常类，用于处理参数验证错误
    """
    def __init__(self, code: int, message: str, error_type: str = "validation_error", **kwargs):
        super().__init__(code, message, error_type, **kwargs)


# 常用错误码定义
class ErrorCode:
    # 系统错误
    SYSTEM_ERROR = 50001
    DATABASE_ERROR = 50002
    NETWORK_ERROR = 50003
    
    # 业务错误
    BUSINESS_ERROR = 40001
    RESOURCE_NOT_FOUND = 40002
    PERMISSION_DENIED = 40003
    QUOTA_EXCEEDED = 40004
    
    # 验证错误
    PARAMETER_INVALID = 40005
    PARAMETER_MISSING = 40006
    VALIDATION_ERROR = 40007
    
    # 认证错误
    AUTHENTICATION_FAILED = 40101
    TOKEN_EXPIRED = 40102
    TOKEN_INVALID = 40103
