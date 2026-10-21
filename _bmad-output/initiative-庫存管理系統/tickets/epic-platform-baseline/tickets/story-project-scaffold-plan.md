---
title: '專案骨架與第一次連線打通'
type: 'feature'
ticket: '1'
created: '2026-10-21'
status: 'draft'
baseline_revision: 'a162a19d2cde1e82eabc6da5b3882924cce95b72'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: ''
review_source: ''
lenses_ran: []
review_loop_iteration: 0
context: ["{project-root}/_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md", "{project-root}/_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/DESIGN.md"]
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 專案沒有任何程式碼——後端、前端、資料庫三者都未接通，E2～E4 沒有可依賴的地基。

**Approach:** 建立 Django 專案與四層設定、連上 `AILearn`、第一組 migration 與統一錯誤包絡；同時建立 Vite + React + TS + Tailwind + shadcn 前端骨架與應用外框（含 TanStack Query），讓 `/api/v1/health` 的回應顯示在前端首頁，形成後端→前端→資料庫的最薄路徑。

## Boundaries & Constraints

**Always:**
- 設定分 base／dev／test／prod 四層，prod 缺 `SECRET_KEY` 或允許主機即啟動失敗（AD-23）
- 憑證只從 `PGPASSFILE` 指向的 `pgpass.conf` 取得；只連 `AILearn` 單一 schema；全部 ORM 參數化查詢（AD-15）
- 錯誤只由單一 DRF handler 回 `{code, detail, field_errors}`，業務錯誤不得回 500；路徑前綴 `/api/v1/`（AD-7、AD-17）
- 介面字串只來自 message catalog（zh-TW 預設、en-US 次要），後端只回機器可讀 `code`（AD-33）
- 色碼、字級、間距、圓角、元件一律取 `DESIGN.md` token；依賴版本依 spine 的 Stack 固定（新增 @tanstack/react-query 5.104.5）

**Never:**
- 不實作登入、權限、帳號、actor、守衛規則（story 2～6 的範圍）
- 不建業務資料表，只建 Django auth 的使用者與群組
- 不做架構守門工具（AD-24 落地於 E2）、不做完整 i18n 框架
- 不引入 spine 未登錄的相依套件；不把憑證、密碼或金鑰寫進任何檔案

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 健康檢查 | GET /api/v1/health | 200 `{"status":"ok","version":"…"}` | DB 不可連時 503 `db.unavailable` |
| 未知路徑 | GET /api/v1/nope | 404 且 body 為統一錯誤包絡 | 集中 handler 轉換 |
| 前端首頁 | 後端已啟動／未啟動 | 顯示版本字串／顯示明確連線失敗與重試鈕 | 不得空白頁 |
| 啟動前置 | 缺 `SECRET_KEY`／`PGPASSFILE` | 啟動即失敗並指出缺哪個 | 不退回預設、不降級連線 |

</frozen-after-approval>

## Code Map

- `backend/config/settings/{base,dev,test,prod}.py` — 四層設定；dev 讀 `PGPASSFILE` 連 `AILearn`
- `backend/core/{exceptions,handler}.py` — 領域例外與單一 DRF exception handler
- `backend/config/{urls,wsgi}.py` — 掛 `/api/v1/`、WhiteNoise、admin
- `backend/accounts/` — Django auth 的 User／Group 與第一組 migration
- `frontend/{package.json,vite.config.ts,tailwind.config.ts,src/index.css}` — 依賴、dev proxy、token 落地
- `frontend/src/{i18n/,features/shell/,pages/HomePage.tsx}` — catalog、外框、版本字串頁
- `README.md` — hitl 步驟（建 venv、裝依賴、migrate、起前後端）
- 不得修改：`_bmad-output/**`、`AGENTS.md`、`PostgreSQL使用說明.md`

## Tasks & Acceptance

**Execution:**
- [ ] `backend/requirements.txt` — django 6.1.2、djangorestframework 3.18.3、psycopg[binary] 3.3.6、whitenoise 6.12.0、waitress 3.0.2
- [ ] `backend/config/settings/{base,dev,test,prod}.py` — 四層設定，prod 缺必要變數即失敗
- [ ] `backend/core/{exceptions,handler}.py` — 統一錯誤包絡 `{code, detail, field_errors}`
- [ ] `backend/config/{urls,wsgi}.py` — 掛 `/api/v1/`、WhiteNoise、admin
- [ ] `backend/accounts/` — auth 的 User／Group 與第一組 migration
- [ ] `backend/accounts/views.py` — `GET /api/v1/health` 回 status 與 version
- [ ] `frontend/package.json` — vite 8.3.4、react 19.3.1、@tanstack/react-query 5.104.5、typescript 5.9.3、tailwind 4、shadcn 相依
- [ ] `frontend/vite.config.ts` — `/api` proxy 至 `http://127.0.0.1:8000`
- [ ] `frontend/tailwind.config.ts`、`frontend/src/index.css` — `DESIGN.md` token 落成 CSS 變數
- [ ] `frontend/src/i18n/` — catalog 與切換，缺翻譯 fallback zh-TW
- [ ] `frontend/src/features/shell/` — 側欄、頂列、使用者選單
- [ ] `frontend/src/pages/HomePage.tsx` — 以 TanStack Query 取 health 顯示版本字串；後端不可達時顯示錯誤與重試
- [ ] `README.md` — hitl 步驟與啟動指令

**Acceptance Criteria:**
- Given 依 README 建立 venv 並安裝依賴，when 執行 `python manage.py migrate`，then `AILearn` 出現 auth 資料表且不需輸入密碼
- Given 後端已啟動，when 請求 `GET /api/v1/health`，then 回應 200 且 body 含 `status` 與 `version`
- Given 後端未啟動，when 開啟前端首頁，then 顯示明確連線失敗訊息與重試鈕而非空白
- Given 前端已載入，when 切換 zh-TW／en-US，then 文字立即改變且頁面未重新整理
- Given prod 設定或 `PGPASSFILE` 缺值，when 啟動，then 失敗並指出缺哪一個
- Given 任一 API 錯誤，when 回應，then body 形狀為 `{code, detail, field_errors}` 且狀態碼符合語意

## Implementation Notes

- 本 story 驗收為手動（啟動前後端看版本字串）；自動化測試骨架於 story 7 建立，故本計畫不含 pytest 任務。
- 正式部署（waitress + build 產物）的實際啟動驗證縮減至後續 story，本 story 只備妥設定。

## Plan Change Log

## Review Triage Log

## Design Notes

- **角色用 Django Group**：AD-5 禁止第二套權限系統，自建角色表會與 auth permissions 並存。
- **health 回 version 字串**：驗收不依賴業務資料，前端首頁有可顯示的跨層結果。
- **錯誤集中單一 handler**：DRF 預設 handler 會改寫 validation error 形狀，破壞統一包絡。
- **設定分四層**：AD-23 要求 prod 缺參數即失敗，單一 settings 容易讓 dev 的 `DEBUG=True` 漏到正式環境。
- **shadcn 以手動 minimal 方式落地**：避免 CLI 互動與大量自動檔案，token 一律對齊 `DESIGN.md`。

## Verification

**Commands:**
- `uv venv .venv && uv pip install -r backend/requirements.txt` — 期望：安裝成功且版本與 spine Stack 一致
- `python manage.py migrate` — 期望：`AILearn` 建立 auth 資料表
- `python manage.py check --settings=config.settings.prod`（缺 `SECRET_KEY` 時）— 期望：失敗並指出缺 `SECRET_KEY`
- `npm run build`（frontend）— 期望：產出 `dist/`

**Manual checks (if no CLI):**
- 開啟 `http://127.0.0.1:5173` → 首頁顯示後端版本字串；切換語系文字改變
- 停止後端 → 首頁顯示明確錯誤與重試鈕
