# 庫存管理系統 - 一鍵上線（Cloudflare 臨時網址）
#
# 1. 若後端未啟動，就以獨立背景程序啟動 Django（127.0.0.1:8000）
# 2. 關掉舊的 Quick Tunnel，再啟動一個新的（不開主控台視窗）
# 3. 解析出公開網址，寫入 上線網址.txt 並顯示
#
# 用法：上線.bat（會呼叫本檔）

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$log = Join-Path $env:TEMP 'cloudflared-live.err'
$urlFile = Join-Path $root '上線網址.txt'
$cloudflared = 'C:\Program Files (x86)\cloudflared\cloudflared.exe'

function Write-Step($text) { Write-Host $text -ForegroundColor Cyan }

# --- 1. backend -----------------------------------------------------
$listening = Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue
if ($listening) {
    Write-Step "[INFO] 後端 (:8000) 已在執行 (PID $($listening[0].OwningProcess))。"
}
else {
    $py = Join-Path $root '.venv\Scripts\python.exe'
    if (-not (Test-Path $py)) {
        Write-Host '[ERROR] 找不到 .venv，無法啟動後端。' -ForegroundColor Red
        exit 1
    }
    Write-Step '[INFO] 啟動 Django (127.0.0.1:8000) ...'
    $env:PGPASSFILE = 'C:\Users\user\Desktop\pgpass.conf'
    Start-Process -FilePath $py `
        -ArgumentList 'manage.py', 'runserver', '127.0.0.1:8000', '--noreload' `
        -WorkingDirectory (Join-Path $root 'backend') `
        -RedirectStandardOutput (Join-Path $env:TEMP 'django-live.out') `
        -RedirectStandardError (Join-Path $env:TEMP 'django-live.err') `
        -WindowStyle Hidden
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue) { break }
    }
    if (-not (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)) {
        Write-Host '[ERROR] Django 啟動失敗，請看 %TEMP%\django-live.err' -ForegroundColor Red
        exit 1
    }
    Write-Step '[INFO] Django 已就緒。'
}

# --- 2. stop the previous quick tunnel --------------------------------
Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" |
    Where-Object { $_.CommandLine -like '*tunnel --url*' } |
    ForEach-Object {
        Write-Step "[INFO] 關閉舊的 Tunnel (PID $($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 2

# --- 3. start a new quick tunnel --------------------------------------
if (-not (Test-Path $cloudflared)) {
    Write-Host "[ERROR] 找不到 cloudflared：$cloudflared" -ForegroundColor Red
    exit 1
}
if (Test-Path $log) { Remove-Item $log -Force }
Write-Step '[INFO] 建立 Cloudflare Quick Tunnel ...'
Start-Process -FilePath $cloudflared `
    -ArgumentList 'tunnel', '--url', 'http://127.0.0.1:8000', '--no-autoupdate' `
    -RedirectStandardOutput (Join-Path $env:TEMP 'cloudflared-live.out') `
    -RedirectStandardError $log `
    -WindowStyle Hidden

function Read-SharedFile($path) {
    # 日誌檔同時被 cloudflared 寫入中，必須以共享模式讀取，否則會被鎖住
    try {
        $fs = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        $sr = New-Object IO.StreamReader($fs)
        $text = $sr.ReadToEnd()
        $sr.Close(); $fs.Close()
        return $text
    } catch {
        return ''
    }
}

$url = $null
for ($i = 0; $i -lt 45 -and -not $url; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path $log) {
        $m = [regex]::Match((Read-SharedFile $log), 'https://[a-z0-9-]+\.trycloudflare\.com')
        if ($m.Success) { $url = $m.Value }
    }
}

if (-not $url) {
    Write-Host "[ERROR] 讀不到 Tunnel 網址，請查看 $log" -ForegroundColor Red
    exit 1
}

Set-Content -Path $urlFile -Value $url -Encoding ASCII
Write-Host ''
Write-Host '================================================' -ForegroundColor Green
Write-Host '  已上線' -ForegroundColor Green
Write-Host "  公開網址：$url" -ForegroundColor Green
Write-Host "  網址檔案：$urlFile" -ForegroundColor Green
Write-Host '  前端頁面與 API 皆由此網址提供' -ForegroundColor Green
Write-Host '================================================' -ForegroundColor Green
Write-Host ''
Write-Host '（網址會隨 cloudflared 重啟而改變；關掉 cloudflared 即下線）'
