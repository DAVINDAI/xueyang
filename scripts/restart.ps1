# 停止8000和5173端口的进程
Write-Host "Stopping existing backend processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Stopping existing  frontend processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force

# 激活虚拟环境
.\backend\venv\Scripts\Activate.ps1

Write-Host "starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "waiting for backend server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; `$env:VITE_API_BASE_URL='http://localhost:8000/api'; npm run dev"