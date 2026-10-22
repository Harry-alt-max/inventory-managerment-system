# AGENTS.md

本檔案提供 AI 助理（OpenCode）在此專案工作時所需的背景知識與規範。
每次開啟此專案時會自動載入，請保持內容精簡且準確。

---

## 專案概述

- **專案名稱**：庫存管理系統
- **專案目的**：管理商品庫存、進出貨記錄與供應商資料
- **目前狀態**：初期建置階段，尚未決定技術堆疊

---

## 環境資訊

### 作業系統
- Windows（win32）
- Shell：PowerShell（Windows PowerShell，**非** PowerShell 7 / pwsh）

### 已安裝的執行環境
| 工具 | 版本 |
|------|------|
| Node.js | v22.18.0 |
| npm | 10.9.3 |
| Python | 3.14.7（miniconda3） |
| PostgreSQL | 18.6 |

---

## 資料庫設定（重要）

### 連線資訊
| 項目 | 值 |
|------|-----|
| 主機 | `localhost` |
| 連接埠 | `5432` |
| 使用者 | `postgres` |
| 主要資料庫 | `AILearn`（**含大寫，大小寫敏感**） |
| psql 完整路徑 | `C:\Program Files\PostgreSQL\18\bin\psql.exe` |

### 密碼處理（已設定自動填入）
- 密碼**不需手動輸入**，已透過 `pgpass.conf` 自動提供
- 密碼檔位置：`C:\Users\user\Desktop\pgpass.conf`
- 環境變數：`PGPASSFILE` = `C:\Users\user\Desktop\pgpass.conf`
- 內容格式：`localhost:5432:*:postgres:<密碼>`（實際值只存在於 `pgpass.conf`，不寫入本文件）

> ⚠️ **不要**在程式碼或文件中硬編碼密碼，也不要主動要求使用者提供密碼，因為已由 `pgpass.conf` 處理。

### 連線指令
```powershell
# 標準寫法（因資料庫名稱含大寫，外層單引號、內層雙引號）
psql -U postgres -d '"AILearn"' -h localhost

# 或使用完整路徑（PATH 可能未在當前 session 生效時）
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d '"AILearn"' -h localhost
```

### 資料庫清單
| 資料庫 | 用途 |
|--------|------|
| `AILearn` | 本專案主要資料庫 |
| `my_first_db` | 測試用（與本專案無關） |
| `postgres` | 系統管理庫 |
| `template0` / `template1` | 系統樣板，**切勿刪除** |

---

## 技術規範與注意事項

### 外部服務環境變數（憑證一律只走環境變數）

| 變數 | 用途 |
|------|------|
| `PGPASSFILE` | PostgreSQL 憑證檔路徑（已設定） |
| `RESEND_API_KEY` | Resend 寄信 API key（**未設定時系統不會寄信**，只記錄） |
| `RESEND_FROM_EMAIL` | 預設寄件人 |
| `NOTIFY_EMAILS` | 系統通知的預設收件者（逗號分隔） |

> 憑證**不可**寫進任何檔案（`base.py`、`.env`、文件、版控）。
> 寄信一律經由 `backend/core/email.py`（唯一寄信入口）。

### PowerShell 環境陷阱（務必注意）
1. **引號處理**：PowerShell 傳參數給外部程式時，引號容易被吃掉。
   - 需要傳入含大寫的識別字時，使用 `'"AILearn"'`（外單內雙）
   - 複雜 SQL 建議寫入 `.sql` 檔，再用 `psql -f 檔案.sql` 執行
2. **`&&` 不支援**：Windows PowerShell 5.x 不支援 `&&`，請分開執行或使用 `;`
3. **輸出中文亂碼**：PowerShell 輸出含中文時常出現亂碼，這是編碼問題，不影響實際執行結果
4. **不要用 `pwsh`**：本機未安裝 PowerShell 7，請使用 `powershell`

### PostgreSQL 規範
1. 識別字**未加引號會自動轉小寫**。若需要保留大小寫，必須始終加雙引號
2. 建立資料庫時若名稱含大寫，之後**所有**連線與 SQL 都必須加引號
3. 連線時務必指定 `-U postgres`，否則會退回使用 Windows 帳號名稱而認證失敗
4. 新增資料表時請使用 UTF8 編碼，並注意資料庫 collation 為 `Chinese (Traditional)_Taiwan.950`

---

## 開發慣例

### 檔案命名
- 文件使用中文名稱（例如 `PostgreSQL使用說明.md`）
- 程式碼檔案使用英文小寫加連字號

### 文件語言
- 與使用者溝通、撰寫文件皆使用**繁體中文**
- 程式碼內註解：可使用繁體中文

### 驗證要求
- 執行資料庫操作後，**必須實際查詢確認結果**，不要只憑指令成功就回報完成
- 建立資料庫／資料表後，用 `\l`、`\dt` 或 `SELECT` 驗證

---

## 相關文件

| 檔案 | 說明 |
|------|------|
| `PostgreSQL使用說明.md` | 給人看的 PostgreSQL 設定與操作說明 |
| `Cloudflare Tunnel使用說明.md` | 內網穿透（Quick Tunnel／具名 Tunnel）設定與安全注意事項 |
| `Resend整合說明.md` | 電子郵件通知（Resend）架構、環境變數與驗證方式 |

---

## 待辦與後續方向

- [ ] 決定技術堆疊（Node.js + Express 或 Python + FastAPI）
- [ ] 設計資料庫結構（商品、庫存、進出貨、供應商）
- [ ] 建立資料表與關聯
- [ ] 開發後端 API
- [ ] 開發前端介面
