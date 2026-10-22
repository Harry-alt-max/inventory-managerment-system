# Resend 電子郵件整合說明

> 說明庫存管理系統如何透過 [Resend](https://resend.com) 寄送通知信，
> 以及要如何在本機設定與驗證。

---

## 一、目前會寄哪些信

| 觸發時機 | 信件 | 程式位置 |
|----------|------|----------|
| 商品入庫（`POST /api/v1/stock/inbound`） | 入庫通知（商品、庫位、批次、數量、操作人） | `backend/stock/services.py` → `receive_stock()` |

寄信是**附帶的副作用**：交易提交後才寄（`transaction.on_commit`），
交易回滾就不會寄；寄信失敗也**不會**讓入庫失敗。

---

## 二、架構

```
view / service
   └─ core/email.py  ← 全系統唯一的寄信入口
        ├─ 沒有 RESEND_API_KEY → 略過（記錄警告 + 內容），不寄
        ├─ 沒有收件者         → 略過（記錄 info）
        └─ 有憑證 → django.core.mail.mailers.default（Resend SMTP）
```

- `backend/core/email.py`
  - `is_provider_configured()`：是否已設定憑證
  - `notification_recipients()`：預設收件者（`NOTIFY_EMAILS`）
  - `send_notification(subject=..., body=..., recipients=None)`：寄信，**回傳布林值、絕不丟例外**
- `backend/config/settings/base.py`：`MAILERS` 設定
- `backend/accounts/management/commands/send_test_email.py`：驗證用指令

### 為什麼用 `MAILERS` 而不是 `EMAIL_BACKEND`

Django 6.1 起以 `MAILERS` 取代 `EMAIL_BACKEND` / `EMAIL_*`（後者將於 Django 2028 移除）：

```python
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": "smtp.resend.com",
            "port": 587,
            "username": "resend",       # Resend 固定帳號
            "password": RESEND_API_KEY, # 就是 API key
            "use_tls": True,
            "timeout": 10,
        },
    }
}
```

沒有 `RESEND_API_KEY` 時，`MAILERS` 退回 `console` backend（內容印在伺服器輸出），
開發環境不需要 Resend 帳號也能運作。

---

## 三、環境變數

| 變數 | 必填 | 說明 |
|------|------|------|
| `RESEND_API_KEY` | 寄信時必填 | Resend API key（`re_` 開頭）。**只能從環境變數讀取，不寫進任何檔案** |
| `RESEND_FROM_EMAIL` | 否 | 預設寄件人，預設 `noreply@example.com` |
| `NOTIFY_EMAILS` | 否 | 系統通知的預設收件者，逗號分隔（例如 `ops@example.com,pm@example.com`） |

### 設定方式（PowerShell）

```powershell
# 寫入使用者層級環境變數（永久生效，重新開終端機後自動載入）
[Environment]::SetEnvironmentVariable("RESEND_API_KEY", "re_xxxxxxxx", "User")
[Environment]::SetEnvironmentVariable("RESEND_FROM_EMAIL", "noreply@yourdomain.com", "User")
[Environment]::SetEnvironmentVariable("NOTIFY_EMAILS", "ops@example.com", "User")
```

> 本專案的開發環境是「本機資料庫 + 本機 API」，
> `RESEND_API_KEY` 請**不要**放進 `.env` 或任何檔案，也不要 commit 進版控。
> 與 `PGPASSFILE` 的作法一致：憑證只存在於環境變數。

---

## 四、Resend 端要先做的事

1. 到 <https://resend.com> 建立帳號
2. 建立 API key（<https://resend.com/api-keys>），權限至少要有 `Sending access`
3. **驗證寄件網域**（<https://resend.com/domains>）：只有驗證過的網域才能寄信。
   Resend 會提供 DNS 記錄（SPF、DKIM、DMARC）要加到 DNS 供應商
4. 未驗證網域時，只能寄到 Resend 自己的測試收件人

---

## 五、驗證

```powershell
# 確認環境變數有生效
$env:RESEND_API_KEY   # 若有值就對了
```

```powershell
cd backend
$env:PGPASSFILE="C:\Users\user\Desktop\pgpass.conf"

# 寄一封測試信（收件者預設取 NOTIFY_EMAILS 第一位）
..\.venv\Scripts\python.exe manage.py send_test_email

# 指定收件者
..\.venv\Scripts\python.exe manage.py send_test_email --to someone@example.com
```

成功時會印出 `測試信已寄出：xxx@example.com`；
失敗時會印出明確原因（未設定 key／無收件者／SMTP 認證失敗）。

也可以在**設定金鑰後**重啟後端，然後做一次入庫，從日誌確認：

```
INFO core.email use_case=send_notification result=sent subject=[庫存管理系統] 入庫通知：... recipients=1
```

---

## 六、常見問題

| 現象 | 原因 | 處理 |
|------|------|------|
| `未設定 RESEND_API_KEY，無法寄信` | 環境變數沒設或沒重開終端機 | 用上面的 `SetEnvironmentVariable` 設定後重開終端機 |
| `SMTPAuthenticationError: (535, ...)` | API key 無效／已被撤銷 | 到 Resend 重新產生 key |
| `550 ... not verified` | 寄件網域未在 Resend 驗證 | 完成網域驗證，或先用 `onboarding@resend.dev` 測試 |
| 日誌顯示 `result=skipped reason=no_recipients` | 沒設定 `NOTIFY_EMAILS` | 設定 `NOTIFY_EMAILS`，或在呼叫時指定 `recipients=` |
| 日誌顯示 `result=skipped reason=missing_api_key` | 沒設定 `RESEND_API_KEY` | 同上；此時內容會一併記錄在日誌中，方便確認格式 |

---

## 七、安全提醒

- **憑證只走環境變數**：不要寫進 `base.py`、`.env`、`.md` 或任何會被 commit 的檔案
  （本專案原則：Never — 不把憑證、密碼或金鑰寫進任何檔案）。
- **通知信會外流**：入庫通知會寄到 `NOTIFY_EMAILS`，內含商品名稱、庫位、數量與操作人。
  若系統是對外開放的（例：Cloudflare 臨時網址），收件人名單請自行斟酌。
- **公開網址 + 示範登入**：開發環境的 `DEMO_ROLE_LOGIN` 開著時，任何拿到網址的人都能操作系統，
  也可能間接觸發通知信。對外開放前請先關閉。
