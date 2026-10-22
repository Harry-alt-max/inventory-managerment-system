@echo off
chcp 65001 >nul
title Inventory System - Go Live (Cloudflare Quick Tunnel)
cd /d "%~dp0"

REM Wrapper: real logic lives in go-live.ps1 (UTF-8 with BOM).
REM Keep this file ASCII-only, CRLF, no BOM.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0go-live.ps1"
echo.
pause
