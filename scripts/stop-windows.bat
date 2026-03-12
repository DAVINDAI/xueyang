@echo off

:: 学氧助手 - Windows 停止脚本
:: 停止所有本地运行的服务

:: 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %GREEN%========================================%NC%
echo %GREEN%  学氧助手 - Windows 停止脚本  %NC%
echo %GREEN%========================================%NC%
echo.

:: 停止 uvicorn 进程
echo %BLUE%正在停止后端服务...%NC%
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq 学氧助手 - 后端服务*" 2>nul
if %errorlevel% equ 0 (
    echo %GREEN%后端服务已停止！%NC%
) else (
    echo %YELLOW%后端服务未运行或已停止。%NC%
)

:: 停止 npm 进程
echo %BLUE%正在停止前端服务...%NC%
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq 学氧助手 - 前端服务*" 2>nul
if %errorlevel% equ 0 (
    echo %GREEN%前端服务已停止！%NC%
) else (
    echo %YELLOW%前端服务未运行或已停止。%NC%
)

echo %GREEN%========================================%NC%
echo %GREEN%  停止完成！  %NC%
echo %GREEN%========================================%NC%
echo.
echo %YELLOW%按任意键退出...%NC%
pause
