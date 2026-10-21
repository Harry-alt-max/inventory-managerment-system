---
title: '專案骨架與第一次連線打通'
type: 'feature'
ticket: '1'
created: '2026-10-21'
status: 'built'
baseline_revision: '2b63f7f24f8b37974bca8acaf52892cf34bb5c2f'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
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
- `frontend/{package.json,vite.config.ts,src/index.css}` — 依賴、dev proxy、token 落地（Tailwind v4 以 CSS `@theme` 定義，不使用 `tailwind.config.ts`）
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
- [ ] `frontend/package.json` — vite 8.3.4、react 19.3.1、@tanstack/react-query 5.104.5、typescript 5.9.3、tailwindcss + @tailwindcss/vite 4.3.3、lucide-react 1.61.0
- [ ] `frontend/vite.config.ts` — `/api` proxy 至 `http://127.0.0.1:8000`
- [ ] `frontend/src/index.css` — Tailwind v4 `@theme` 落 `DESIGN.md` token 成 CSS 變數
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
- 環境陷阱：`PGPASSFILE` 只在使用者層設定，當前行程的 process 層為空——執行 `manage.py`、`psql` 等需要連線的指令前，先在該 shell 設定 `$env:PGPASSFILE='C:\Users\user\Desktop\pgpass.conf'`。
- 前端 `npm install` 與後端 `uv venv`／`uv pip install` 需要網路；`shadcn/ui` 元件以手動 minimal 方式建立（不跑 shadcn CLI），token 一律對齊 `DESIGN.md`。
- **補上自動化測試（超出原計畫，因 build 流程的 Matrix Test Audit 要求矩陣每列都有跑過的測試）**：新增 `backend/requirements-dev.txt`（pytest 9.1.1、pytest-django 4.14.0、factory-boy 3.3.3，版本取自 spine Stack）、`backend/pytest.ini`、`backend/tests/test_api_contract.py`、`backend/tests/test_settings_guards.py`，共 9 個測試全數通過，覆蓋矩陣第 1（health 200／DB 不可連 503）、第 2（未知路徑 404 統一包絡）、第 4（缺 SECRET_KEY／PGPASSFILE 啟動即失敗）三列；測試使用獨立測試庫 `AILearn_test`，不連 `AILearn`。
- 矩陣第 3 列（前端首頁）目前以**手動驗證**覆蓋：啟動 Vite dev server 與 Django 後，`/api/v1/health` 經 proxy 回 200 JSON，首頁顯示後端版本字串；停止後端後 proxy 回 502／ECONNREFUSED，前端映射為 `network.unreachable` 並顯示錯誤卡與重試鈕。前端自動化測試待 story 7 決定測試工具後補上。
- 首次執行測試時有 2 個失敗（DB 存取未加 `django_db` 標記、prod 檢查順序先撞 `DB_NAME` 而非 `PGPASSFILE`），已修正後通過。
- 實作代理另說明兩處與計畫的差異：`AUTH_USER_MODEL` 改為 `accounts.User` 但資料表沿用 `auth_user`（讓 accounts 擁有第一組 migration 又維持慣例表名）；WhiteNoise 以 middleware 掛載而非包在 `wsgi.py` 外層。兩者皆不違反 spine，已接受。

## Plan Change Log

## Review Triage Log

| # | 位置 | 發現 | 判定 | 證據 | 路由 |
|---|---|---|---|---|---|
| 1 | `backend/config/urls.py:25-29` | `spa_fallback` catch-all 會把 `/assets/*` 也回成 index.html，正式環境 JS/CSS 載不到；`/api/v2/*` 誤回 200 HTML | **high** | `frontend/dist/index.html` 引用 `/assets/index-*.js`；`STATICFILES_DIRS=[]` 且 `frontend/dist` 不在 `STATIC_ROOT` 下，WhiteNoise 無從供應；catch-all 在字串層即命中 | patch |
| 2 | `backend/config/settings/base.py:142` | `CompressedManifestStaticFilesStorage` 未跑 `collectstatic` 前 `/admin/` 拋 `Missing staticfiles manifest entry` | **medium** | Django admin 模板經 `{% static %}` 解析；`test.py` 已降級但 `dev.py`/`prod.py` 走 base | patch |
| 3 | `backend/config/settings/prod.py:55-57` | `SECURE_SSL_REDIRECT` 預設開啟且 `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` 硬寫 True，本機純 HTTP 的正式環境全部 301 到無人接管的 https，session/CSRF cookie 也不會回送 | **high** | spine 環境表：正式（本機）= waitress + WhiteNoise，純 HTTP；README 未列 `SECURE_SSL_REDIRECT` | patch |
| 4 | diff 動到 `_bmad-output/**` | 違反計畫 Code Map 的「不得修改 `_bmad-output/**`」 | **false** | 動到的是 spine 的 Stack 補版本、計畫本身的 status/Code Map/task 行——皆為 build 流程中父層（我）的計畫與 spine 維護，非實作者所為；實作者未動任何 `_bmad-output` 檔案 | — |
| 5 | `backend/tests/**`、README | 測試檔不在該份 diff（diff 產生於我補測試之前）、測試數 9→8、README 未寫測試步驟、pytest 需先匯出 `PGPASSFILE` | **部分 false / low** | 測試數：pytest 實跑輸出 `9 passed`（參數化計 2 次），敘述正確；diff 過期已由重產 diff 修正。README 缺測試步驟與 `PGPASSFILE` 提示為真 | patch（僅 README 部分） |
| 6 | `frontend/src/i18n/catalog.ts:56-67` | 後端可回的多個錯誤碼（`request.method_not_allowed`、`request.not_acceptable`、`request.unsupported_media_type`、`request.throttled`、`resource.duplicate`、`stock.insufficient`）在 catalog 無對應條目，落到 `error.unknown` | **medium** | `core/handler.py:39-51` 與 `core/exceptions.py:84-97` 的碼集合 ⊄ catalog 的 `error.*` 鍵 | patch |
| 7 | `frontend/src/features/shell/Sidebar.tsx:24`、`UserMenu.tsx:34,48`、`HomePage.tsx:56` | 元件內硬寫可見字串（`庫`、`U`、`—`），未走 message catalog | **low** | AD-33：所有使用者可見字串一律來自 catalog | patch |
| 8 | `frontend/src/features/shell/Sidebar.tsx:21`、`frontend/index.html:5` | 側欄固定 `w-58` 無 1024–1279px 圖示列變體；viewport 釘 `width=1280` 使該區間永遠不會出現 | **medium** | DESIGN.md 斷點行為表要求 1024–1279px 摺疊為圖示列 | patch |
| 9 | `frontend/src/pages/HomePage.tsx:55` | 後端版本字串用了 `text-accent-text`，而該 token 依 DESIGN.md 只供「毛利數值文字」 | **low** | DESIGN.md Colors 表：`accent-text` 用途為毛利數值文字 | patch |
| 10 | 計畫 Implementation Notes | 宣稱的測試與該份 diff 不符 | **false** | 見 #5：diff 過期，非宣稱不實 | — |
| 11 | diff 產物 | diff 中文字為亂碼 | **產物問題** | `git diff \| Out-File` 經 PowerShell 以主控台編碼重編碼；改用 `git diff --output` 直接寫原始位元組即修正 | 已修（重產 diff） |

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
