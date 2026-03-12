@echo off

:: 学氧助手 - Windows 重启脚本
:: 停止并重新启动所有服务

:: 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %GREEN%========================================%NC%
echo %GREEN%  学氧助手 - Windows 重启脚本  %NC%
echo %GREEN%========================================%NC%
echo.

:: 停止服务
echo %BLUE%正在停止服务...%NC%

:: 停止 uvicorn 进程
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq 学氧助手 - 后端服务*" 2>nul
if %errorlevel% equ 0 (
    echo %GREEN%后端服务已停止！%NC%
) else (
    echo %YELLOW%后端服务未运行或已停止。%NC%
)

:: 停止 npm 进程
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq 学氧助手 - 前端服务*" 2>nul
if %errorlevel% equ 0 (
    echo %GREEN%前端服务已停止！%NC%
) else (
    echo %YELLOW%前端服务未运行或已停止。%NC%
)

echo.
echo %BLUE%服务停止完成，正在重新启动...%NC%
echo.

:: 项目根目录
set "PROJECT_ROOT=%~dp0.."
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "VENV_DIR=%PROJECT_ROOT%\venv"

:: 日志文件
set "LOG_DIR=%PROJECT_ROOT%\logs"
mkdir "%LOG_DIR%" 2>nul
set "BACKEND_LOG=%LOG_DIR%\backend.log"
set "FRONTEND_LOG=%LOG_DIR%\frontend.log"

:: 检查虚拟环境
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo %RED%错误: 虚拟环境不存在！%NC%
    echo %YELLOW%请先创建虚拟环境：%NC%
    echo python -m venv venv
    pause
    exit /b 1
)

:: 激活虚拟环境
echo %BLUE%正在激活虚拟环境...%NC%
call "%VENV_DIR%\Scripts\activate"
if %errorlevel% neq 0 (
    echo %RED%错误: 激活虚拟环境失败！%NC%
    pause
    exit /b 1
)
echo %GREEN%虚拟环境激活成功！%NC%
echo.

:: 检查后端依赖
echo %BLUE%正在检查后端依赖...%NC%
pip install -r "%BACKEND_DIR%\requirements.txt" --index-url https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo %RED%错误: 安装后端依赖失败！%NC%
    pause
    exit /b 1
)
echo %GREEN%后端依赖检查完成！%NC%
echo.

:: 检查前端依赖
echo %BLUE%正在检查前端依赖...%NC%
cd "%FRONTEND_DIR%"
npm install
if %errorlevel% neq 0 (
    echo %RED%错误: 安装前端依赖失败！%NC%
    pause
    exit /b 1
)
echo %GREEN%前端依赖检查完成！%NC%
echo.

:: 启动后端服务
echo %BLUE%正在启动后端服务...%NC%
cd "%PROJECT_ROOT%"
start "学氧助手 - 后端服务" cmd /c "call "%VENV_DIR%\Scripts\activate" && cd "%BACKEND_DIR%" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > "%BACKEND_LOG%" 2>&1"

:: 等待后端启动
ping 127.0.0.1 -n 5 >nul

:: 启动前端服务
echo %BLUE%正在启动前端服务...%NC%
start "学氧助手 - 前端服务" cmd /c "cd "%FRONTEND_DIR%" && npm run dev > "%FRONTEND_LOG%" 2>&1"

echo %GREEN%========================================%NC%
echo %GREEN%  服务重启成功！  %NC%
echo %GREEN%========================================%NC%
echo.%GREEN%后端服务: http://localhost:8000%NC%
echo.%GREEN%前端服务: http://localhost:5173%NC%
echo.%BLUE%后端日志: %BACKEND_LOG%%NC%
echo.%BLUE%前端日志: %FRONTEND_LOG%%NC%
echo.%YELLOW%按任意键查看日志...%NC%
echo.

:: 查看日志
pause
type "%BACKEND_LOG%"
echo.
echo %YELLOW%========================================%NC%
echo %YELLOW%  前端日志  %NC%
echo %YELLOW%========================================%NC%
echo.
type "%FRONTEND_LOG%"
echo.
echo %GREEN%重启完成！按任意键退出...%NC%
pause
