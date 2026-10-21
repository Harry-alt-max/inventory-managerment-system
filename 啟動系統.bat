@echo off
chcp 65001 >nul
title 庫存管理系統 - 啟動
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [錯誤] 找不到虛擬環境 .venv
  echo 請先在專案根目錄執行：uv venv .venv
  echo 並安裝依賴：uv pip install -r backend\requirements.txt
  pause
  exit /b 1
)

echo 正在啟動後端 (Django :8000) ...
start "後端 Django :8000" cmd /k "cd backend && set PGPASSFILE=C:\Users\user\Desktop\pgpass.conf && ..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"

echo 正在啟動前端 (Vite :5173) ...
start "前端 Vite :5173" cmd /k "cd frontend && npm run dev"

timeout /t 6 /nobreak >nul
start "" "http://127.0.0.1:5173"

echo.
echo ================================================
echo  系統已啟動
echo    前端（開這個）  http://127.0.0.1:5173
echo    後端 API       http://127.0.0.1:8000/api/v1/health
echo.
echo  首次使用請先建立資料：
echo    manage.py seed_demo   （建立四種職能的示範帳號）
echo  關掉上面兩個視窗即可停止系統。
echo ================================================
pause
