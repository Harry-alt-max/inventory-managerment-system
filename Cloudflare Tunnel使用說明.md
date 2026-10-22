# Cloudflare Tunnel（內網穿透）使用說明

> 本文件說明如何用 Cloudflare Tunnel 把本機的庫存管理系統（Django 後端 :8000）
> 透過公網網址開放，讓人在外網也能存取。

---

## 一、已安裝的軟體

| 工具 | 版本 | 位置／說明 |
|------|------|-----------|
| cloudflared | 2026.10.3 | `C:\Program Files (x86)\cloudflared\cloudflared.exe`（winget 安裝） |
| Cloudflare CLI (`cf`) | 0.15.0 | `npm install -g cf` 全域安裝 |
| Cloudflare MCP | — | 設定於 `~/.config/opencode/opencode.jsonc` |
| Cloudflare Skills | — | `~/.agents/skills`（`agents-sdk`、`basin`） |

---

## 二、一鍵上線（Quick Tunnel）

執行專案根目錄的：

```
上線.bat
```

腳本（實際邏輯在 `go-live.ps1`）會：

1. 檢查後端 `:8000` 是否在跑，沒有就以**獨立背景程序**啟動 Django（`--noreload`）
2. 關掉舊的 Quick Tunnel，再啟動一個新的（不開主控台視窗，關掉工作階段也不會斷）
3. 解析出公開網址，寫入 `上線網址.txt`（已加入 `.gitignore`）並顯示：

```
https://xxxxx-yyyy-zzzz.trycloudflare.com
```

開啟該網址即可從外網存取整個系統（前端頁面與 API 同源）。

想看 Tunnel 的即時輸出時，可手動執行：

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8000 --no-autoupdate
```

> **`.bat` / `.ps1` 的編碼陷阱（踩過的坑）**
> - `.bat` 必須是 **CRLF 換行**。只有 LF 換行時，`cmd.exe` 會把整個檔案解析成一團亂碼，
>   出現 `'oudflared' 不是內部或外部命令` 之類的怪訊息。
> - `.bat` **不能有 UTF-8 BOM**。有 BOM 時第一行會變成 `'﻿@echo' 不是內部或外部命令`。
> - `.bat` 的 `REM` 註解與 `if (...)` 區塊內盡量只放 ASCII；中文放在單獨的 `echo` 行最安全。
>   （多行位元組字元會讓 `cmd.exe` 的位元組／字元計數錯位，行首被吃掉。）
> - `.ps1` 在 Windows PowerShell 5.1 讀取時，**必須有 UTF-8 BOM** 才會以 UTF-8 解碼；
>   沒有 BOM 會把中文解成亂碼，甚至讓字串結尾被吃掉而導致解析錯誤。
> - 中文訊息顯示需要 `chcp 65001`（`.bat` 開頭）。
> - 讀取被 `Start-Process -RedirectStandardError` 鎖住的日誌時，
>   要用 `FileShare.ReadWrite` 開檔（`[IO.File]::ReadAllText` 會直接丟 IOException）。

### Quick Tunnel 的限制
- 網址**每次啟動都會變**，無法固定
- 不需要 Cloudflare 帳號，但**沒有 SLA／可用性保證**
- 只適合臨時測試、要讓人快速看一下

---

## 三、Django 端必須做的設定（已設定好）

`backend/config/settings/dev.py` 已加入：

```python
ALLOWED_HOSTS = [
    ...,
    ".trycloudflare.com",   # 允許 Quick Tunnel 的主機名稱
]

CSRF_TRUSTED_ORIGINS = [
    ...,
    "https://*.trycloudflare.com",
]
```

> **注意**：Django 6.x 的 `ALLOWED_HOSTS` 已不支援 `*.example.com` 這種星號寫法，
> 必須改用「前導點」寫法 `.trycloudflare.com`（代表網域本身與其所有子網域）。
> 若寫成 `*.trycloudflare.com`，會出現 `DisallowedHost`（HTTP 400）。

---

## 四、正式環境怎麼做（具名 Tunnel）

若要固定網址（例如 `https://inventory.example.com`），需改用具名 Tunnel：

1. 準備一個已托管在 Cloudflare 的網域
2. `cloudflared tunnel login`（瀏覽器授權，選擇網域）
3. `cloudflared tunnel create inventory-tunnel`
4. 建立設定檔 `~/.cloudflared/config.yml`：

```yaml
tunnel: <TUNNEL_ID>
credentials-file: C:\Users\user\.cloudflared\<TUNNEL_ID>.json
ingress:
  - hostname: inventory.example.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

5. `cloudflared tunnel route dns inventory-tunnel inventory.example.com`
6. `cloudflared tunnel run inventory-tunnel`
7. 安裝為 Windows 服務，讓它開機自動啟動：

```powershell
cloudflared service install
```

> 用具名 Tunnel 時，`ALLOWED_HOSTS` 要改成你的固定網域（例如 `inventory.example.com`），
> `CSRF_TRUSTED_ORIGINS` 也要一併更新。

---

## 五、目前狀態

### 目前上線中的臨時網址

```
https://absent-hang-online-infant.trycloudflare.com
```

> 網址每次用 `上線.bat` 重跑都會不同；隨時可看 `上線網址.txt`。

- 服務：Django（`127.0.0.1:8000`）同時提供 API 與前端建置產物（`frontend/dist`）
- cloudflared 以**獨立背景程序**執行（不依附於工作階段），日誌在 `%TEMP%\cloudflared-live.err`
- Django 以**獨立背景程序**執行（`--noreload`，日誌在 `%TEMP%\django-live.err`）

### 已實測通過的流程

| 測試 | 結果 |
|------|------|
| `GET /api/v1/health` | 200 `{"status":"ok"}` |
| `GET /` | 200（前端 SPA 頁面） |
| `GET /assets/index-*.js` / `*.css` | 200 |
| `GET /api/v1/auth/csrf` → `POST /api/v1/auth/login-as` | 200，取得 session |
| `GET /api/v1/auth/me` | 200（回傳登入者與角色） |
| `GET /api/v1/items` / `warehouses` / `stock` / `stock/movements` / `batches` | 200 皆有資料 |
| `GET /admin/` | 302（導向登入，正常） |

> 用 `curl` 測試 JSON 端點時注意：Windows 上傳 JSON 給 curl 容易壞掉引號，
> 建議把 body 寫成**無 BOM 的 UTF-8 檔案**再用 `--data-binary @檔名` 送出；
> 用 `Set-Content -Encoding UTF8` 會帶 BOM，DRF 會回 `request.invalid`。

### 前端與後端

- 前端建置產物需與後端同源由 Django 提供：`npm run build`（產物在 `frontend/dist`）
- 前端 `API_BASE` 為相對路徑 `/api/v1`，因此經由 Tunnel 存取時**不需要**改設定
- 前端目前只有 1 筆商品／1 座倉庫／1 筆庫存與進貨紀錄（示範資料）

---

## 六、安全提醒

- 本專案開發環境開啟了 `DEMO_ROLE_LOGIN`（可直接選角色登入），
  **一旦 Quick Tunnel 對外開放，等於任何拿到網址的人都能登入**。
- 對外開放前請先關閉 `DEMO_ROLE_LOGIN`（設為 `False`），或改用具名 Tunnel
  並加上 Cloudflare Access（Zero Trust）做身分驗證。
- `ALLOWED_HOSTS` 的放行僅限 `dev.py`（開發環境），正式環境 `prod.py` 不受影響。
