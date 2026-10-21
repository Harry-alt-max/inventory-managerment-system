@echo off
chcp 65001 >nul
title 庫存管理系統 - 停止
cd /d "%~dp0"

echo 正在停止後端 (:8000) 與前端 (:5173) ...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1

echo 已停止。
timeout /t 2 /nobreak >nul
