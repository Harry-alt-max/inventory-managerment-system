# 庫存管理系統

內部進銷存後台（庫存管理、進出貨記錄、供應商資料）。

目前狀態：**專案骨架與第一次連線已打通**（後端 Django + 資料庫 `AILearn` + 前端 Vite/React）。
登入、權限、角色、庫存與銷貨等業務功能尚未實作（見 `_bmad-output/initiative-庫存管理系統/tickets/`）。

---

## 技術堆疊

| 層 | 技術 | 版本 |
| --- | --- | --- |
| 後端 | Python / Django | 3.14.7 / 6.1.2 |
| 後端 | djangorestframework / psycopg / WhiteNoise / waitress | 3.18.3 / 3.3.6 / 6.12.0 / 3.0.2 |
| 資料庫 | PostgreSQL（單一 schema：`AILearn`） | 18.6 |
| 前端 | Vite / React / TypeScript | 8.3.4 / 19.3.1 / 5.9.3 |
| 前端 | Tailwind CSS v4 / @tanstack/react-query / lucide-react | 4.3.3 / 5.104.5 / 1.61.0 |

---

## 目錄結構

```text
backend/
  config/            # 設定（base/dev/test/prod 四層）、urls、wsgi、asgi
  core/              # 共用層：例外、單一錯誤 handler、版本、view
  accounts/          # Django auth 的使用者與群組（第一組 migration）
frontend/
  src/i18n/          # message catalog（zh-TW 預設、en-US 次要）與語系切換
  src/features/shell/# 應用外框：側欄、頂列、使用者選單
  src/pages/         # HomePage：顯示後端版本字串
  src/components/ui/ # 最小 shadcn 風格元件（button / card / badge）
```

---

## 前置條件

- Node.js 22.18.0、npm 10.9.3
- Python 3.14.7、uv 0.13.4
- PostgreSQL 18.6 已啟動，且存在資料庫 `AILearn`（含大寫，大小寫敏感）
- 憑證檔 `pgpass.conf` 已存在，格式：`localhost:5432:*:postgres:<密碼>`

---

## 步驟一：設定環境變數

憑證只由 `PGPASSFILE` 指向的 `pgpass.conf` 提供，**密碼不得寫入任何檔案**。
目前環境只在「使用者層」設定了 `PGPASSFILE`，當前 shell 的 process 層為空，
因此每個新開的 PowerShell 視窗都要先執行一次：

```powershell
$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'
```

---

## 步驟二：後端

```powershell
# 1. 建立虛擬環境（專案根目錄）
uv venv .venv --python "C:\Users\user\miniconda3\python.exe"

# 2. 安裝依賴
uv pip install --python .venv\Scripts\python.exe -r backend\requirements.txt

# 3. 套用 migration（會在 AILearn 建立 auth 與 accounts 資料表）
cd backend
..\.venv\Scripts\python.exe manage.py migrate

# 4. 啟動開發伺服器（127.0.0.1:8000）
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

開發層設定為 `config.settings.dev`（`manage.py` 的預設值）。
若 `SECRET_KEY` 未設定，開發層會改用「本次行程的暫時金鑰」，每次重啟即失效（僅供開發）。

> **設計決定**：`AUTH_USER_MODEL` 指向 `accounts.User`（Django `AbstractUser`），
> 資料表沿用慣例名稱 `auth_user`，角色沿用 Django auth 的 `Group`（AD-5：不建第二套權限系統）。
> 後續 story 若需在使用者上加欄位（例如帳號代號），可直接追加 migration。

### 檢查設定分層

```powershell
# 正式設定缺 SECRET_KEY 時必須直接失敗並指出缺哪一個
$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'
..\.venv\Scripts\python.exe manage.py check --settings=config.settings.prod
```

正式環境（`config.settings.prod`）需要的環境變數，缺任何一項都會在啟動時失敗、不退回預設值：

| 環境變數 | 說明 |
| --- | --- |
| `SECRET_KEY` | 正式環境金鑰 |
| `ALLOWED_HOSTS` | 允許的主機，逗號分隔 |
| `DB_NAME` | 正式環境資料庫名稱（正式需明確指定，不沿用開發的 `AILearn`） |
| `PGPASSFILE` | `pgpass.conf` 路徑（由 base 層檢查） |

正式環境另有以下選用變數：

| 環境變數 | 預設 | 說明 |
| --- | --- | --- |
| `SECURE_SSL` | `0` | 設為 `1` 時才啟用 HTTPS 強制轉向（`SECURE_SSL_REDIRECT`）與安全 cookie（session／CSRF）。本機以 waitress + WhiteNoise 走**純 HTTP** 部署時請維持 `0`，否則會被 301 轉到沒有任何終端的 https，且 session／CSRF cookie 不再送出 |
| `SECURE_HSTS_SECONDS` | `0` | HSTS 有效期（秒），僅在對外提供 HTTPS 時才有意義 |

---

## 步驟三：前端

```powershell
cd frontend
npm install
npm run dev        # http://127.0.0.1:5173
```

開發時 Vite 會把 `/api` 轉送 `http://127.0.0.1:8000`（`frontend/vite.config.ts`），
前端與後端維持同源，session + CSRF 才能直接運作。

正式建置（產物由 Django + WhiteNoise 同源供應）：

```powershell
npm run build      # 產出 frontend/dist/
```

正式環境以 waitress + WhiteNoise 部署時，靜態檔案需要先收集一次（正式層使用
`CompressedManifestStaticFilesStorage`，未收集會缺少 manifest 而無法供應檔名雜湊）：

```powershell
# 前端建置
cd frontend
npm install
npm run build

# 後端收集靜態檔（產出 backend/staticfiles/）
cd ..\backend
..\.venv\Scripts\python.exe manage.py collectstatic --noinput

# 啟動正式環境（本機純 HTTP；SECURE_SSL 保持 0）
$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'
$env:SECRET_KEY='<正式金鑰>'
$env:ALLOWED_HOSTS='127.0.0.1'
$env:DB_NAME='AILearn'
..\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8000 config.wsgi:application
```

---

## 測試

測試使用 pytest + pytest-django，位於 `backend/tests/`，設定檔為 `backend/pytest.ini`
（`DJANGO_SETTINGS_MODULE = config.settings.test`）。
測試設定繼承 base 層的 `PGPASSFILE` 檢查，**必須先匯出 `PGPASSFILE`**，否則 pytest 會在
import 階段就失敗；測試使用獨立資料庫 `AILearn_test`（由 pytest 建立 `test_` 前綴的暫存庫），
**不會連到 `AILearn`**（AD-14）。

```powershell
# 1. 安裝測試用相依（不進正式環境）
uv pip install --python .venv\Scripts\python.exe -r backend\requirements-dev.txt

# 2. 匯出憑證檔位置（每個新 shell 都要重複一次）
$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'

# 3. 執行測試（在 backend/ 目錄下執行）
cd backend
..\.venv\Scripts\python.exe -m pytest
```

只跑特定檔案：

```powershell
..\.venv\Scripts\python.exe -m pytest tests\test_api_contract.py
```

---

## 驗收檢查

| 檢查 | 指令／動作 | 預期 |
| --- | --- | --- |
| 資料庫 | `manage.py migrate` | `AILearn` 出現 `auth_*`（`auth_user`／`auth_group`／`auth_permission`）與 `django_*` 資料表，且不需輸入密碼 |
| 健康檢查 | `curl http://127.0.0.1:8000/api/v1/health` | `200` `{"status":"ok","version":"0.1.0"}` |
| 未知路徑 | `curl http://127.0.0.1:8000/api/v1/nope` | `404` `{"code":"resource.not_found","detail":"...","field_errors":{}}` |
| 其他 API 前綴 | `curl http://127.0.0.1:8000/api/v2/nope` | `404` 且同樣是統一錯誤包絡（不回落 SPA HTML） |
| 前端資源 | `curl -I http://127.0.0.1:8000/assets/index-*.js` | `200` 且 `Content-Type` 為 `text/javascript`（不是 HTML） |
| 前端首頁 | 開啟 `http://127.0.0.1:5173` | 顯示後端版本字串 `0.1.0` |
| 語系切換 | 頂列切換 zh-TW / en-US | 文字立即改變，頁面不重新整理 |
| 後端未啟動 | 停止後端後重新整理首頁 | 顯示明確的連線失敗訊息與「重新檢查」鈕（不是空白頁） |
| 前端建置 | `npm run build` | 產出 `frontend/dist/` |

---

## 疑難排解

- **`ImproperlyConfigured: 缺少必要的環境變數 PGPASSFILE`**
  目前 shell 未設定 process 層環境變數，先執行
  `$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'`。
- **psql / 連線相關指令也會需要同一個環境變數**，原因相同。
- **PowerShell 顯示中文亂碼**：屬於主控台編碼問題，不影響實際執行結果；
  需要正確輸出時可先執行 `chcp 65001`。
- **Windows PowerShell 5.x 不支援 `&&`**，請分開執行指令。
