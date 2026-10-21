# Web 驗證審查 — 庫存管理系統 Architecture Spine

- 審查對象：`_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`
- 審查面向：所有「## Stack」表列出的技術與版本，以及文件中任何地方出現的其他技術／工具名稱（原始碼樹、環境表、AD 中的工具）
- 審查日期：2026-10-21
- 方法：以 PyPI JSON API、npm registry API、官方文件（docs.djangoproject.com、pytest-django readthedocs、vite.dev、whitenoise.readthedocs.io、postgresql.org、python.org）、GitHub Releases API 實際查證；並以唯讀 shell 指令確認本機環境

---

## 0. 結論摘要

**判定：需修正（4 個硬性問題、5 個版本落後問題、1 個環境事實錯誤）**

Stack 表中有 3 個 pin 是「不存在」或「與其他 pin 互相矛盾」的硬傷：`psycopg 3.3.7`（PyPI 上不存在，僅有未發布的 3.3.7.dev1）、`djangorestframework 3.17.1`（不支援 spine 自己 pin 的 Django 6.1）、`pytest-django 4.11.1`（早於 Python 3.14 官方支援）。另有 `gunicorn` 在 spine 的「正式（本機）」列中，但本機是原生 Windows，而 gunicorn 在原生 Windows 上無法執行。

此外，本次逐項查證過程中**沒有發現任何一項 pin 是 beta、RC 或 EOL 線**——所有被 pin 的版本本身都真實存在且是穩定版；問題全部是「落後太多」或「互相不相容」。

---

## 1. Stack 表逐項查證

| 技術 | spine 的 pin | 網路查證的當前版本 | 判定 | 建議 |
| --- | --- | --- | --- | --- |
| Python | 3.14.7 | 3.14.7 為 3.14 系列最新維護版（2026-08-05 釋出，7 個 maintenance release） | **OK** | 維持 3.14.7（與本機一致） |
| Django | 6.1 | PyPI latest = **6.1.2**（2026-10-06）；另有 6.1.1（2026-09-02）、6.1（2026-08-05）。官方文件已寫「supports Python 3.12/3.13/3.14/3.15 (as of 6.1.3)」，但 6.1.3 尚未上 PyPI | **OK（系列正確），pin 太粗** | 改 pin 為 **6.1.2**（現行 patch）；「6.1」在 lockfile 中會浮動到 6.1.2，但文件層級應寫明確 patch |
| djangorestframework | 3.17.1 | **3.18.3**（2026-10-06）。3.18.0（2026-08-07）release notes 明確列出「Add support for Django 6.1」並「Drop support for Django 4.2, 5.0, 5.1」；3.18.2 另含 3 項安全修補（GHSA-33wh-fxxf-88vv、GHSA-3547-9m27-7rxg、GHSA-xw6w-gcfp-cf8m） | **不相容，必須改** | 改為 **3.18.3**。理由：DRF 3.17.x 最高只支援 Django 6.0，與本 spine pin 的 Django 6.1 互斥；3.17.2 亦存在安全修補 |
| psycopg | 3.3.7 | PyPI latest = **3.3.6**（psycopg / psycopg-binary 同為 3.3.6，2026-09-18）。3.3.7 僅存在於官方文件的「unreleased」段落（3.3.7.dev1） | **不存在，必須改** | 改為 **3.3.6** |
| PostgreSQL | 18.6 | 18.6 為 18 系列最新 minor（postgresql.org release notes 已列 18.6）；19 目前只有 RC 1（2026-10-15），尚未 GA | **OK** | 維持 18.6；Django 6.1 支援 PostgreSQL 15+，18 沒問題（6.1 已棄用 PG 14） |
| Node.js | 22.18.0 | 22.18.0 確實存在；但 22.x 最新為 **22.23.3**，另 24.x（最新 24.22.0）為 active LTS、26.x（26.12.0）為 current | **OK 但落後** | 至少升到 **22.23.3**；若要 current LTS 可用 24.x。Vite 8 的 engines 為 `^20.19.0 || >=22.12.0`，22.18.0 與 22.23.3 皆滿足 |
| Vite | 8.0 | npm `latest` = **8.3.4**（vite.dev 文件版本標示亦為 v8.3.4）；8.0 確實存在 | **OK（系列正確）但落後** | 改為 **8.3.4**。Vite 8.3.4 engines = `^20.19.0 \|\| >=22.12.0`，本機 Node 22.18.0 滿足；`server.port` 預設 **5173**（已於 v8.3.4 文件確認）與 spine 一致 |
| React | 19.2.7 | npm `latest` = **19.3.1**；19.2.x 系列存在 19.2.0–19.2.9（19.2.7 確實存在） | **OK 但落後** | 改為 **19.3.1**（需一併 pin `react-dom` 19.3.1，spine 目前漏列） |
| TypeScript | 5.9.2 | npm `latest` = **7.0.2**（2026-07-08，Go 原生版）；JS 過渡線最新 **6.0.3**（2026-04-16）；5.x 線最後一版 **5.9.3**（2025-09-30） | **存在但明顯落後** | 建議 **6.0.3**（保留 JS 實作、生態相容性最佳）或 **7.0.2**（現行 latest，編譯快 8–12 倍，但 7.0 尚無穩定 programmatic API，7.1 才補）。至少應升 5.9.3。`typescript` 的 engines 對 Node 22 無限制 |
| pytest | 8.4.2 | PyPI latest = **9.1.1**；8.4.x 為上一個系列（8.4.2 本身存在，2025 年釋出） | **OK 但落後** | 改為 **9.1.1**（requires_python >=3.10，與 Python 3.14 相容） |
| pytest-django | 4.11.1 | PyPI latest = **4.14.0**（2026-08-10）。changelog：4.12.0（2026-02-14）才「Official Python 3.14 support」+「Official Django 6.0 support」；4.13.0 drop Django 4.2/5.1；4.14.0 處理 Django 6.2 的 `ImproperlyConfigured` | **不相容，必須改** | 改為 **4.14.0**。4.11.1（2025-04-03）早於 Python 3.14 官方支援，與 spine pin 的 Python 3.14.7 與 Django 6.1 皆不匹配；其 `requires_dist` 亦無 `django>=5.2` 下界 |
| factory_boy | 3.3.3 | PyPI latest = **3.3.3**（仍是最新版）；requires_python >=3.8；相依 faker latest 40.43.0 | **OK** | 維持 3.3.3 |
| WhiteNoise | 6.12.0 | PyPI latest = **6.12.0**（2026-02-26/27），djangopackages 標示 Production/Stable；文件 Requirements 寫「Django 4.2 to 6.1 supported」；requires_python >=3.10 | **OK** | 維持 6.12.0（與 Django 6.1 相容） |
| gunicorn | 25.3.0 | PyPI latest = **26.2.0**；25.3.0 存在但落後 | **落後 + 環境錯誤，必須改** | 版本改 **26.2.0**；但更關鍵的是 **gunicorn 不支援原生 Windows**（官方網站標題即「Python WSGI HTTP Server for UNIX」；issue #2865 維護者回覆「windows is not supported at the moment」；Flask 文件「It does not support Windows (but does run on WSL)」）。本專案環境為原生 Windows → 正式環境改用 **waitress**（或 uvicorn），或明確要求以 WSL 執行 |

---

## 2. 文件其他位置出現的技術名稱查證

### 2.1 AD-16 / 環境表：「Vite dev server（:5173），`/api` 走 proxy」
- **已驗證**：Vite 8.3.4 `server.port` 預設值 = `5173`（vite.dev/config/server-options）。
- **補充**：Vite 8 預設 `server.host` = `'localhost'`；`server.proxy` 為 Vite 原生功能，spine 的 `vite.config.ts` proxy 設計成立，無需額外套件。

### 2.2 AD-16：「前端為 Vite + React + TypeScript」
- **重大遺漏**：Vite 跑 React 必須安裝 `@vitejs/plugin-react`，但 spine 的 Stack 表完全未列。npm latest = **6.1.2**，其 `peerDependencies` = `vite ^8.0.0`、`oxc-transform-react ^0.152.0`、`@rolldown/plugin-babel ^0.1.7 || ^0.2.0`、`babel-plugin-react-compiler ^1.0.0`（Vite 8 已由 esbuild 改用 Oxc，故需上述 peer）。
- 同樣未列：`react-dom`（latest 19.3.1，必須與 react 同版）、`@types/react`、`@types/react-dom`。Vite 8 不再內建 React fast refresh 轉換，這些都得顯式宣告。
- 建議：在 Stack 表補上 `@vitejs/plugin-react 6.1.2`、`react-dom 19.3.1`（或直接以「React 19.3.1 + react-dom 19.3.1 + @vitejs/plugin-react 6.1.2」成組列出）。

### 2.3 環境表：「正式（本機）| gunicorn + WhiteNoise」
- **錯誤**（詳見 §1 最後一列）：本機為 Windows（AGENTS.md 載明 win32 / Windows PowerShell），gunicorn 在原生 Windows 不支援。同一列還寫「正式以 `npm run build` 產出靜態檔，由 Django（WhiteNoise）同源供應」——WhiteNoise 部分正確（6.12.0 支援 Django 6.1），但 WSGI server 選項需改成 waitress/uvicorn 或加註「僅在 WSL/Linux 執行 gunicorn」。

### 2.4 AD-14：「pytest + pytest-django + factory_boy」
- 版本問題已在 §1 記載。額外注意：`pytest-django` 4.14.0 起新增 `django` extra（`pip install pytest-django[django]` 可讓解析器自動選到相容的 Django 版本下界），建議直接採用。
- `factory_boy` 3.3.3 需搭配 `faker`（latest 40.43.0），spine 未列 faker，屬可接受的隱式相依。

### 2.5 AD-15 / 環境表：PostgreSQL + `PGPASSFILE` / `pgpass.conf`
- **本機實測（唯讀）**：
  - `psql --version` → `psql (PostgreSQL) 18.6` ✅ 與 pin 相符。
  - `[Environment]::GetEnvironmentVariable('PGPASSFILE','User')` → `C:\Users\user\Desktop\pgpass.conf`，且 `Test-Path` 為 True ✅。
  - **注意**：目前這個 review shell 的 process 層 `PGPASSFILE` 為空字串（User 層已設定，但未繼承到既有行程）。因此直接跑 `psql` 會卡在密碼提示；補上 `$env:PGPASSFILE="C:\Users\user\Desktop\pgpass.conf"` 後連線成功，`select current_database();` 回傳 `AILearn` ✅。spine AD-15 的敘述正確，但建議在文件中註明新開終端機才會繼承。
- 資料庫名稱含大寫，psycopg 連線時 `dbname` 需帶引號（`"AILearn"`），spine 未明寫，實作時易踩雷。

### 2.6 Django 6.1 的版本面風險（皆已用官方文件確認）
- Django 6.1（2026-08-05 釋出）mainstream support 至 2027-04、extended 至 2027-12 → 屬**當前支援系列**，不是 EOL。
- Django 6.1 已移除 PostgreSQL 14 支援（保留 15+）→ 本機 18.6 無礙。
- Django 6.1 支援 psycopg 3.2+（`inspectdb` HStore 判斷明載 psycopg 3.2+）→ psycopg 3.3.6 符合。
- Django 6.1 對 `EMAIL_BACKEND` 系列 setting 發出 deprecation、將於 Django 2028 以 `MAILERS` 取代；本專案 v1 未涉及寄信需求，無影響，但若 E1 帳號流程要寄信需留意。
- Django 6.1 新增 `Permission.name`/`codename` 改名時的 migration 行為變更 → AD-5 權限矩陣以 codename 宣告的做法不受影響。

### 2.7 pytest / pytest-django 與 Python 3.14 的相容性鏈
- pytest 9.1.1：requires_python >=3.10 ✅；官方 changelog 標示已加入 Python 3.14 官方支援。
- pytest-django 4.14.0：requires_dist = `pytest>=7.0.0`、`django>=5.2`（僅在 `django` extra 下）→ 對 pytest 9.1.1 與 Django 6.1.2 都成立 ✅。
- pytest-django 4.11.1：無 `django>=5.2` 下界，且官方在 4.12.0 才宣告 Python 3.14 支援 → spine pin 與 Python 3.14.7 不符 ❌。

### 2.8 TypeScript 的現實風險
- TS 5.9.2（2025-07-31）存在 ✅，但同系列已有 5.9.3（2025-09-30）。
- 現行 latest = TS 7.0.2（Go 原生移植，2026-07-08 GA）。官方公告明示：**7.0 不提供穩定的 programmatic API，至少要到 7.1**。對本專案（Vite 8 以 Oxc 轉譯、不依賴 TS compiler API）影響有限，但若後續導入需要 TS API 的工具鏈，應先選 6.0.3（JS 過渡線，2026-04-16）。
- TS 6.0.3 / 7.0.2 的 engines 分別為 `>=14.17` / `>=16.20.0`，Node 22.18.0 皆滿足。

---

## 3. 本機環境實測結果（唯讀）

| 項目 | spine 記載 | 實測 | 結果 |
| --- | --- | --- | --- |
| Python | 3.14.7 | `python --version` → Python 3.14.7 | ✅ 一致 |
| Node.js | 22.18.0 | `node --version` → v22.18.0 | ✅ 一致（但落後 22.23.3 / 24.x LTS） |
| npm | 未列 | 10.9.3 | — |
| PostgreSQL | 18.6 | `psql (PostgreSQL) 18.6` | ✅ 一致 |
| 資料庫 | `AILearn` | `select current_database();` → `AILearn` | ✅ 存在 |
| `PGPASSFILE` | 指向 `pgpass.conf` | User 層 = `C:\Users\user\Desktop\pgpass.conf`（檔案存在）；本 review 行程的 process 層為空 | ⚠️ 需在新終端機／顯式匯出 |

---

## 4. 發現清單（依嚴重度）

### 必須修正（會導致安裝失敗或不相容）

1. **psycopg 3.3.7 不存在** → 3.3.6。
   證據：PyPI `psycopg` 與 `psycopg-binary` latest 皆為 3.3.6（2026-09-18）；官方 news 頁寫「Psycopg 3.3.7 (unreleased)」、文件版本標題為「3.3.7.dev1」。
2. **djangorestframework 3.17.1 與 Django 6.1 不相容** → 3.18.3。
   證據：DRF 3.18.0 release notes（2026-08-07）「Add support for Django 6.1」；3.17.x 只宣告 Django 6.0。另 3.18.2 含三項安全修補。
3. **pytest-django 4.11.1 早於 Python 3.14 官方支援** → 4.14.0。
   證據：pytest-django changelog v4.12.0（2026-02-14）「Official Python 3.14 support / Official Django 6.0 support」；v4.13.0 drop Django 4.2、5.1；v4.14.0 為 latest。
4. **gunicorn 在原生 Windows 無法執行**，但 spine 環境表把它列為「正式（本機）」的 WSGI server。
   證據：gunicorn 官網標題「Python WSGI HTTP Server for UNIX」；GitHub issue #2865 維護者「windows is not supported at the moment」；Flask 官方文件「It does not support Windows (but does run on WSL)」。
   建議：正式環境列改為 `waitress`（純 Python、跨平台、WSGI）或 `uvicorn`；若堅持 gunicorn，須明寫「需於 WSL/Linux 執行」。

### 應更新（版本落後，但不改也能跑）

5. **DRF / pytest / pytest-django** 見上；另：
6. **pytest 8.4.2 → 9.1.1**（8.4.x 為上一系列）。
7. **Vite 8.0 → 8.3.4**（現行文件版本即 8.3.4）。
8. **React 19.2.7 → 19.3.1**（並補 `react-dom` 19.3.1）。
9. **TypeScript 5.9.2 → 6.0.3 或 7.0.2**（現行 latest 為 7.0.2；若求穩妥先 6.0.3；最低限度 5.9.3）。
10. **gunicorn 25.3.0 → 26.2.0**（若最終改用 waitress 則整列移除）。
11. **Django 6.1 → 6.1.2**（把系列 pin 收斂為 patch pin）。
12. **Node.js 22.18.0 → 至少 22.23.3**（或明載 24.x LTS）。Node 22 仍在維護期，Vite 8 要求 ^20.19 || >=22.12，本機版本已滿足，非阻斷項。

### 建議補充（Stack 表缺漏，greenfield 需注意 starter 的實際依賴）

13. `@vitejs/plugin-react`（Vite 8 + React 必備，latest 6.1.2，peer `vite ^8.0.0`）— spine 完全未提。
14. `react-dom`（latest 19.3.1）、`@types/react` — spine 只列 React。
15. Vite 8 已由 esbuild 遷移至 Oxc（rolldown），`@vitejs/plugin-react` 6.x 需 `oxc-transform-react`、`@rolldown/plugin-babel`、`babel-plugin-react-compiler` 等 peer；greenfield 建置時需照 peer 指示安裝，否則 build 會失敗。
16. `faker`（factory_boy 的相依）未列。
17. psycopg 在 Windows 的安裝形式建議明寫 `psycopg[binary]`（psycopg-binary 有 Windows wheel），避免落到需要編譯 libpq 的 `psycopg[c]`。
18. 環境表的 port 與連線細節：`Vite :5173` 已確認為現行預設；`manage.py runserver :8000` 為 Django 預設；Django 靜態檔正式環境除 WhiteNoise 外另需 `collectstatic`，spine 未提及該步驟（流程性，非版本性）。

### 無法以網路確認 / 僅能部分確認者

- **Django 6.1.3**：Django 官方文件（6.1 release notes）已寫「supports Python 3.12, 3.13, 3.14, and 3.15 (as of 6.1.3)」，但 PyPI 上截至 2026-10-21 最新仍為 **6.1.2**。推測 6.1.3 尚未發佈或文件先行。已採 6.1.2 為建議 pin。
- **psycopg 3.3.7**：官方文件標題即為 `3.3.7.dev1`，news 頁列「3.3.7 (unreleased)」→ 判定為未發布。
- **factory_boy 對 Django 6.1 的官方支援矩陣**：factory_boy 3.3.3 的文件只寫「supports active Python versions / Django's supported versions」這種泛用敘述，無逐版矩陣；因其與 ORM 解耦（僅依賴 faker），判定可用，但未取得逐版官方背書。
- **Vite 8.3.4 對 React 19.3 的官方測試矩陣**：未找到逐版相容性表；以 `plugin-react` peer `vite ^8.0.0` 與 React 19.3 的 npm 發布時序推斷相容，屬推論而非官方背書。

---

## 5. 建議的 Stack 表（修正後）

| Name | Version | 變更說明 |
| --- | --- | --- |
| Python | 3.14.7 | 不變（= 目前 3.14 最新） |
| Django | 6.1.2 | 收斂為 patch pin |
| djangorestframework | 3.18.3 | **改**（支援 Django 6.1 + 含安全修補） |
| psycopg | 3.3.6 | **改**（3.3.7 不存在；建議安裝 `psycopg[binary]`） |
| PostgreSQL | 18.6 | 不變（18 系列最新 minor） |
| Node.js | 22.23.3 | **改**（22.x 最新；Vite 8 engines 已滿足） |
| Vite | 8.3.4 | **改** |
| @vitejs/plugin-react | 6.1.2 | **新增**（Vite 8 + React 必備） |
| React / react-dom | 19.3.1 | **改**（19.2.7 落後） |
| TypeScript | 6.0.3（或 7.0.2） | **改**（5.9.2 落後；7.0.2 尚無穩定 API） |
| pytest | 9.1.1 | **改** |
| pytest-django | 4.14.0 | **改**（官方 Python 3.14 支援自 4.12.0 起） |
| factory_boy | 3.3.3 | 不變（= 最新） |
| WhiteNoise | 6.12.0 | 不變（= 最新，支援 Django 4.2–6.1） |
| waitress（或 gunicorn，僅 WSL/Linux） | 3.0.2 / 26.2.0 | **改**：正式環境的 WSGI server 需可在 Windows 執行 |

---

## 6. 附註

- 本次審查未修改 spine 檔案，亦未對本機資料庫做任何寫入（僅執行 `select current_database()` 讀取）。
- 所有「網路查證」均附具可複核的來源：PyPI JSON API、npm registry API、GitHub Releases API、docs.djangoproject.com、pytest-django readthedocs、whitenoise.readthedocs.io、vite.dev、postgresql.org、python.org、gunicorn.org。
