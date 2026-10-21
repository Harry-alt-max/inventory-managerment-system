# 架構 Spine 審查（Good-spine Checklist 檢核）

- **受審文件**：`_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`（type: architecture-spine, purpose: build-substrate, altitude: feature, status: draft）
- **驅動票據**：`_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md`（R1–R20、Constraints C1–C9、Done when 1–5）
- **來源 PRD**：`prd-inventory-management-system/prd-inventory-management-system.md`（FR-1～FR-20、§4.6、§5、§6、§7、§8）、`addendum.md`（§A–§G）
- **審查角度**：Good-spine checklist（涵蓋真實分歧點、Rule 可強制且真能阻止所述分歧、Deferred 安全、命名技術為現行版本、與既有程式碼相容、覆蓋驅動票據、承接父層 spine 不被削弱、每個維度都必須被決定／延後／列為開放問題）
- **專案性質**：課業規模、greenfield（無既有程式碼）、單一開發者小組、單機部署
- **審查日期**：2026-10-21

---

## 0. 結論

**判定：退回修訂（Needs Revision）— 尚未達可接受門檻。**

架構骨架的「形狀」是對的：分層單體 + service 層、四 app 對應四 epic、單向依賴 `sales → stock → catalog`、FIFO 成本基準、僅追加稽核、統一錯誤包絡，這些都是真正能防止分歧的決定，方向與 PRD 拍板事項一致，且不與既有程式碼衝突（greenfield，僅與既有 `AILearn` 資料庫／`pgpass.conf` 環境相容，這點處理正確）。

但門檻未過的原因有兩類：

1. **覆蓋缺口**：R1、R7、R10、R12、R15、R16、R18 等多項需求的關鍵規則，在 Capability→Architecture map 中雖有列，但實際查核後**沒有任何一條 AD 的 Rule 真正涵蓋**，等於把分歧點留給下游兩支 team（accounts / stock / sales）各自拍板。
2. **整個維度留白**：正式／正式環境的設定與秘密管理（operational envelope）雖有「環境」表，但沒有任何 AD 決定 `DEBUG`／`SECRET_KEY`／`ALLOWED_HOSTS`／dev 與正式共用同一資料庫的處理；同時 spine 完全沒有 Open Questions 章節，PRD §8 的未決事項沒有任何一條被承接。

嚴重度統計：**Critical 0、High 8、Medium 15、Low 5**。

---

## 1. Good-spine Checklist 逐條檢核

| 檢核項 | 判定 | 說明 |
| --- | --- | --- |
| 為下層（epic/story）修好真實分歧點且不遺漏 | **部分通過** | app 邊界、依賴方向、service 層唯一寫入入口、FIFO、僅追加、錯誤包絡、編號規則都修好了；但 R1 鎖定、R7/R10 唯一鍵、R12 用途列舉、R15 調貨來源建議、R16 銷貨單狀態機等分歧點未被任何 Rule 覆蓋（見 §3、§4） |
| 每條 AD 的 Rule 可強制、且真能阻止其所述分歧 | **部分通過** | AD-7／9／11／12／13／15／17 的 Rule 可透過 schema／程式碼檢查強制；AD-1／2／3／8／12／13／14 的 Rule 目前只有「慣例」而無任何強制機制（無 import-linter／django-architectural-rules／架構測試），可被靜默違反（見 H7） |
| Deferred 之下不會讓兩個單位分歧 | **通過** | Deferred 8 項皆為純工程優化或 PRD 明確排除項（容器化、CI/CD、報表、監控、備份、前端狀態管理、多租戶、行動端、i18n），不影響後端契約與資料語意；唯一有風險的是「備份與復原」與稽核永久保存的張力（L1） |
| 命名的技術為現行版本 | **不通過** | `psycopg 3.3.7` 在 PyPI 上不存在（最新為 3.3.6），照 pin 安裝會失敗；`Django 6.1` + `djangorestframework 3.17.1` 是不受支援的組合（DRF 3.17.1 的 classifier 只到 Django 6.0，支援 6.1 需 3.18.3）（見 H6、H9） |
| 與既有（brownfield）程式碼相容而非牴觸 | **通過（無既有程式碼）** | greenfield，無 brownfield 可牴觸；與既有環境（`AILearn` 單庫、`pgpass.conf`／`PGPASSFILE`）相容，符合 addendum §C、§D 與 initiative Constraint 2、9 |
| 若由票據驅動，覆蓋票據每一條需求 | **不通過** | 見 §2 覆蓋表：R1、R7、R10、R12、R15、R16、R18 的核心語意無 AD 實質涵蓋；另 ticket Constraints C1（參數化查詢）、C5（效能基準）亦無對應 Rule |
| 若承接父層 spine，未削弱或牴觸繼承決策 | **不適用** | `parent: none`，本層為根 spine |
| 每個 altitude 擁有的維度都已決定／延後／列為開放問題 | **不通過** | operational/environmental envelope 只決定了一半（環境表有，但正式環境設定、秘密管理、資料庫環境分離無 AD）；且 spine 完全沒有 Open Questions 章節，PRD §8 的 6 條未決事項（客戶寄貨是否計毛利、折扣是否可疊加、退貨流程、多供應商、編碼格式、部門＝角色）全部失蹤（見 H8） |

---

## 2. R1–R20 覆蓋度分析

「地圖有列」不等於「被涵蓋」。下表的「實質涵蓋」判定標準是：**至少有一條 AD 的 Rule 文字直接規定該需求的關鍵行為**。

| R | 需求要點 | 地圖所列 AD | 實質涵蓋 | 判定 |
| --- | --- | --- | --- | --- |
| R1 | 登入、統一錯誤訊息、**失敗 5 次鎖 15 分鐘** | AD-1,5,6,17 | AD-6 只定 session+CSRF；AD-17 只定錯誤包絡格式 | **缺口**：鎖定計數、鎖定窗口、鎖定時的統一回應（「帳號或密碼錯誤」）無任何 Rule（H1） |
| R2 | 四角色權限矩陣、越權拒絕、會計唯讀 | AD-1,5 | AD-5 明文 | 覆蓋 |
| R3 | 異動／銷貨帶非空操作人員且與登入者一致 | AD-3,12,18 | AD-18 記錄操作人員，但未禁止由 client 傳入 | **部分**：actor 來源未約束（M1） |
| R4 | 商品主檔、`INV-`+6 碼、必填拒儲 | AD-1,2,8 | AD-8 定編號；AD-7 有 `field_errors` 通道 | 覆蓋（驗證細節由 story 決定可接受） |
| R5 | 名稱部分關鍵字查詢、位置／數量／倉庫、空結果、加總一致 | AD-2,3,14 | 無排序與比對語意 | **缺口**：精確名稱優先、空結果不是錯誤、最小關鍵字長度未定（M2） |
| R6 | 異動含正負號、用途、批次、不可改刪 | AD-3,12,18 | 僅追加有明文 | **部分**：正負號約定、移轉／調貨兩筆紀錄的產生時點僅隱含（M3） |
| R7 | 供應商、統編／名稱必填、**同統編不得重複** | AD-1,8 | AD-8 只管編號與主鍵 | **缺口**：唯一性規則無 AD（H2） |
| R8 | 整數水位、低於水位清單、缺口、補貨後離開清單 | AD-2,3,14 | 三條 AD 皆無「水位規則」文字 | **缺口**：清單語意、水位預設 0、欄位歸屬（catalog 欄位 vs stock 規則）皆未定（H2'→M6） |
| R9 | 批次、PO 號、單價數量、總價自動算、缺值拒儲 | AD-1,8,11 | AD-8 定編號與不可改 | **部分**：缺單價／數量拒儲、批次數量與入庫量關係、批次可先建未到貨（M4） |
| R10 | 倉庫（唯一編碼）、位置（同倉代碼唯一）、列出位置商品 | AD-1,8 | AD-8 不含倉庫／位置 | **缺口**：唯一性與代碼格式（H2、M5） |
| R11 | 入庫指定批次、單價取自批次、缺值拒絕 | AD-3,4,11,14 | AD-11 只涵蓋 FIFO 結算 | **部分**：入庫必須指定批次、單價不得於入庫端輸入（M4） |
| R12 | 領用、用途（客戶寄貨／臨時出貨）、不得超領、**不計毛利** | AD-3,4,14 | AD-4 只禁「領用掛銷貨用途」 | **缺口**：用途列舉與毛利排除規則無 AD（H4） |
| R13 | 同倉移轉、移出移入同步、總量不變 | AD-3,4 | AD-4 只說跨倉必須有調貨單 | **部分**：「移轉限同倉」未明文（M6） |
| R14 | 調貨單、移出移入兩筆、總量不變、可回溯單據 | AD-3,4,14 | 明文 | 覆蓋（一單一目標倉、免審批未定，M7） |
| R15 | 可售狀態、各倉可用量、**建議調貨來源倉庫**、無庫存標示 | AD-2,4 | 無任何 Rule 觸及「建議來源」 | **缺口**（H3） |
| R16 | 多商品組合、**同一商品不重複**、**可存草稿**、送出才扣減 | AD-3,4,9,14 | 無銷貨單狀態機 | **缺口**（H5） |
| R17 | 一階百分比折扣、0–100% 拒儲、兩位小數 | AD-7,9 | AD-9 有 Decimal/捨入 | **部分**：一階不疊加、範圍、表示法（10% 記為 0.1）未明文（M8） |
| R18 | 毛利＝折後金額−成本（FIFO）、**無成本紀錄顯示「成本未設定」**、建議售價 | AD-9,11 | FIFO 有明文 | **部分**：null 成本語意、建議售價／預計毛利欄位歸屬未定（M9） |
| R19 | 銷貨紀錄欄位、依日期／銷貨單號查詢、不可刪、僅沖銷 | AD-3,12,18 | 沖銷與不可刪有明文 | **部分**：查詢契約與銷貨單號格式未定（M10） |
| R20 | 建帳、指派角色、停用、���密；停用不可登入、紀錄保留 | AD-5,6 | 未明文停用語意 | **部分**（M11） |

> **票據 Constraints 覆蓋**：C2 憑證（AD-15）、C3 交易完整性（AD-3/4）、C4 僅追加（AD-12）、C6 銷貨唯一入口（AD-4）、C7 跨倉走調貨單（AD-4）有對應；**C1 參數化查詢無 AD**（M14）；**C5 效能基準（1,000 商品／10,000 異動／2 秒）無 AD**，Deferred 以「靠索引即可達成」一句帶過（M13）；C8 角色固定四種僅隱含於 AD-5；C9 一庫一 schema 有 AD-15。

---

## 3. 發現清單

### 3.1 Critical（0）

無。本次未發現會使整份 spine 失效、或與 PRD 拍板事項直接矛盾（例如成本基準、成本來源）的事實性錯誤。

### 3.2 High（8）

**H1｜R1 登入鎖定機制完全未被涵蓋**
- **位置**：Capability→Architecture Map 第 226 行（R1 → AD-1, AD-5, AD-6, AD-17）；AD-5（第 67–71 行）、AD-6（第 73–77 行）、AD-17（第 139–143 行）
- **問題**：PRD FR-1 與 initiative R1 明訂「同一帳號連續失敗 5 次暫時鎖定 15 分鐘」與「一律回應『帳號或密碼錯誤』」。spine 三條相關 AD 沒有任何一條規定失敗計數存在哪裡（DB 表 / cache / 行程內記憶體）、鎖定窗口如何跨越行程重啟、以及鎖定期間的統一回應。這是 accounts 與 ops 層之間的真實分歧點：兩種實作（例如一個用 Django cache、一個用 model）行為一致但無法互通，且重啟後行為不同。
- **具體修法**：新增 **AD-19 — 登入失敗計數與鎖定**：規則寫明「失敗計數與鎖定到期時間以 DB model 儲存（欄位：`failed_attempts`、`locked_until`）；連續 5 次失敗後鎖定 15 分鐘；鎖定期內與失敗時的回應訊息字串完全相同（『帳號或密碼錯誤』），不得回應『帳號已鎖定』或透露帳號是否存在；鎖定到期或成功登入即歸零計數」。並在 R1 地圖列補上 AD-19。

**H2｜R7／R10 的唯一性規則無任何 AD 承載**
- **位置**：Map 第 232 行（R7 → AD-1, AD-8）、第 235 行（R10 → AD-1, AD-8）；AD-8（第 85–89 行）
- **問題**：AD-8 的 Rule 只規範「商品編號 `INV-`+6 碼」與「批次流水號 `PO-YYYYMMDD-序號`」的產生與不可修改，並不涉及供應商統編、倉庫編碼、位置代碼。PRD FR-7／FR-10 的硬性驗收條件是「同統編不得重複」「倉庫編碼唯一」「同倉位置代碼唯一」。沒有 AD 規定這些唯一鍵落在哪一層（form 驗證 / DB unique constraint / 兩者都要）、以及重複時錯誤如何指回既有資料，採購與倉管兩支 unit 會各自實作，資料層可能出現重複統編。
- **具體修法**：新增 **AD-20 — 資料唯一性約束落於資料庫**：規則寫明「下列鍵在資料庫層以 UNIQUE constraint 表達，不僅靠應用層驗證：供應商.統一編號、倉庫.倉庫編碼、Location.(warehouse, location_code)、商品.商品編號、批次.批次流水號；應用層檢查命中既有資料時回應 AD-7 的 `field_errors` 並指回既有資料；唯一鍵欄位一律不可修改」。並在 R7、R10 地圖列補上 AD-20。

**H3｜R15「建議調貨來源倉庫」的選擇規則未決定**
- **位置**：Map 第 240 行（R15 → AD-2, AD-4）；AD-2、AD-4 全文
- **問題**：PRD FR-15 的驗收條件是「各倉可用量加總不得大於總庫存」且「標示建議調貨的來源倉庫」。但「建議」如何算（可用量最大？距離最近？倉碼序最小？是否排除已被訂購量？）在 spine 中完全沒有規則，AD-2（依賴方向）與 AD-4（守衛規則）都沒有文字涉及。銷售 unit 需要一個確定函式來算「建議來源」，若不給，兩人實作會得到不同建議，測試也無從斷言。
- **具體修法**：新增 **AD-21 — 可售狀態與建議調貨來源**：規則寫明「`available = STOCK_LEVEL.qty − 已在草稿或已提交銷貨單鎖定量`；建議來源倉庫 = 可用量大於 0 且可用量最大者，同量時取倉庫編碼字典序最小者；所有倉可用量加總不得大於總庫存；無任何倉可用時回應明確『無庫存』狀態碼而非空陣列」。

**H4｜R12 領用用途集合與「領用不計毛利」未被規則化**
- **位置**：Map 第 237 行（R12 → AD-3, AD-4, AD-14）；AD-4（第 61–65 行）
- **問題**：AD-4 只規定「銷售用途的庫存扣減只能經銷貨 use case（領用用途不得為『銷貨』）」，這是單向的負向禁令，沒有正面列出允許的領用用途（PRD 定義僅「客戶寄貨」「臨時出貨」兩種），也沒有規定領用產生的異動不得進入毛利計算。PRD §8.1 第 1 項「客戶寄貨是否視為已銷貨並計毛利」至今是未決問題；spine 既沒有把它列為 Open Question，也沒有在 Rule 中定案，stock 與 sales 兩支 unit 會各自決定，而此決定直接影響毛利數字。
- **具體修法**：在 AD-4 追加兩句：「領用用途為固定列舉 `客戶寄貨` / `臨時出貨`，其他值一律拒收；領用與同倉移轉、跨倉調貨產生的異動一律不進入毛利計算」；同時在 spine 新增「Open Questions」章節，承接 PRD §8.1 第 1 項（若尚未由使用者拍板）。

**H5｜R16 銷貨單狀態機與「同一商品不重複」未被定義**
- **位置**：Map 第 241 行（R16 → AD-3, AD-4, AD-9, AD-14）
- **問題**：四條 AD 沒有任何一條定義銷貨單本身的狀態（草稿／已送出／已沖銷）與狀態轉移規則，也沒有規定「同一商品不重複列示」的唯一約束，以及草稿期間庫存是否鎖定。PRD FR-16 明訂「可先存草稿（尚未扣減庫存）」，而 AD-3 的「寫入一律在 transaction.atomic() 內」與 AD-12 的僅追加語意都無法推導出草稿與已送出的差別。若 sales unit 自行決定草稿也產生異動紀錄，就會違反 FR-6／SM-2 的帳面等式。
- **具體修法**：新增 **AD-22 — 銷貨單狀態機**：規則寫明「`SALES_ORDER.status ∈ {draft, submitted, reversed}`；draft 不產生銷貨紀錄、不產生庫存異動、不扣減庫存；submitted 在單一 `transaction.atomic()` 內寫入銷貨紀錄與庫存異動並扣減庫存；reversed 僅能由 submitted 經反向沖銷流程產生，並保留原紀錄；同一張單內 `item` 唯一（DB UNIQUE (order, item)）」。並在 R16 地圖列補上 AD-22。

**H6｜正式環境與秘密管理（operational envelope）只決定了一半**
- **位置**：AD-15（第 127–131 行）、Stack 表（第 159–176 行）、「環境」表（第 214–220 行）
- **問題**：「環境」表已列出開發／測試／正式三個環境與其啟動方式，卻沒有任何 AD 決定正式環境的 Django 設定：`DEBUG` 必須為 False、`SECRET_KEY` 的產生與保存位置、`ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS`／同源設定、以及正式與開發共用同一個 `AILearn` 資料庫（開發測試資料與正式資料混存）要如何隔離。AD-15 只處理了資料庫密碼（`PGPASSFILE`），應用層秘密完全留白；Consistency Conventions 也只列出 `DJANGO_SETTINGS_MODULE` 與 `PGPASSFILE` 兩個環境變數。兩個 unit（後端、前端／部署）會各自產生一份 settings，導致正式環境可能帶著 `DEBUG=True` 上線。
- **具體修法**：新增 **AD-23 — 環境設定與秘密管理**：規則寫明「設定分層為 `settings/base.py` + `settings/dev.py` + `settings/prod.py`，以 `DJANGO_SETTINGS_MODULE` 選擇；正式環境 `DEBUG=False`、`ALLOWED_HOSTS` 為明確白名單、`SECRET_KEY` 由環境變數注入且不得落版控（產出時寫入未版控的 `.env` 或由環境變數提供）；正式環境使用與開發不同的資料庫（或至少以獨立 schema／`AILearn_prod` 區隔並定義種子資料清理政策）；憑證一律經環境變數注入，程式碼不得含預設值」。並把「環境」表補上設定來源欄。

**H7｜關鍵結構 AD 只有慣例、沒有強制機制**
- **位置**：AD-1、AD-2、AD-3、AD-12、AD-13、AD-14
- **問題**：這六條 AD 承擔了整份 spine 的大部分防分歧價值（app 邊界、單向依賴、service 層唯一寫入入口、僅追加封鎖、migration 唯一路徑），但沒有一條說明它們「如何被強制」。目前只能在 code review 時人工察覺違規；AD-3 甚至禁止 view/serializer 直接 `save()`，這在 Python 中沒有任何語言層防線。Django ORM 仍可讓 `StockMovement.objects.filter(...).delete()` 生效（AD-12 說「於 manager 層封鎖」，但未禁止取得原始 queryset）。也就是說，AD-3 與 AD-12 的 Rule 在沒有工具的情況下可被靜默違反——這正是 checklist 所指的「Rule 不真正阻止所述分歧」。
- **具體修法**：新增 **AD-24 — 架構約束的自動化強制**：規則寫明「以 `import-linter`（或 `django-architectural-rules`）在 CI 與本機測試中強制 AD-1／AD-2 的依賴方向（catalog 不得依賴 stock／sales、stock 不得依賴 sales）；以 `django-architectural-rules` 或自訂 AST 檢查強制 AD-3（view／serializer 不得 import model 的 save/update/delete 呼叫，寫入僅經 `services.py`）；AD-13 以 `makemigrations --check` 與「從空庫一次跑完」測試強制；上述檢查失敗即視為 build 失敗」。並把該檢查納入 AD-14 的測試紀律。

**H8｜spine 完全沒有 Open Questions 章節，PRD §8 未決事項全部失蹤**
- **位置**：全篇（文件僅有 Design Paradigm／Invariants & Rules／Consistency Conventions／Stack／Structural Seed／Capability→Architecture Map／Deferred 七節）
- **問題**：checklist 明確要求「每個 altitude 擁有的維度都已決定、延後，或列為開放問題」。PRD §8 有 6 條未決事項、initiative Notes 也列了 4 條 Open question（客戶寄貨是否計毛利、折扣是否可疊加、退貨流程、會計報表深度、多供應商欄位、編碼格式、部門＝角色），spine 一條都沒有承接，也沒有宣告「已由本 spine 決定」或「已明確延後」。現況下下游會各自去猜：例如退貨流程未定，但 AD-12 已宣告「取消銷貨以反向沖銷紀錄表達」，很容易被誤讀成退貨已支援。
- **具體修法**：在 Deferred 之前新增 **「Open Questions」** 章節，逐條列出：項目、來源（PRD §8.x）、影響範圍、等待者、暫定處理。例如「退貨流程是否納入 v1（PRD §8.3 第 7 項）— 暫定：v1 不支援退貨，僅支援 AD-12 的反向沖銷；等待者：epic-sales-and-margin」「倉庫與位置編碼格式（PRD §8.2 第 6 項）— 暫定採用 `A1` / `A-03`，若公司規則不同需調整 AD-8／AD-20 的欄位格式」。已在 spine 中被規則抵定的項目，標註「已由 AD-x 解決」。

**H9｜Stack 表命名版本有誤且組合不受支援**
- **位置**：Stack 表（第 159–176 行）
- **問題**：兩個具體事實問題（已對 PyPI 實際查證）：
  1. `psycopg 3.3.7` **在 PyPI 上不存在**（最新為 3.3.6），照表 pin 安裝會直接失敗，setup 無法完成。
  2. `Django 6.1` + `djangorestframework 3.17.1` 是不受支援的組合：DRF 3.17.1 的 trove classifier 只宣告到 `Framework :: Django :: 6.0`，對 Django 6.1 的相容性需 DRF 3.18.3（其 classifier 含 Django 6.1）。
  另外 pytest 8.4.2 / pytest-django 4.11.1 / gunicorn 25.3.0 均為次於現行最新（9.1.1 / 4.14.0 / 26.2.0）的版本——這些不必然是錯（pin 較舊版本本身合法），但 spine 未標示「已驗證鎖定於此版本、升級另行決策」，也無 `requirements.txt`／lockfile 的約束規則。
- **具體修法**：Stack 表改為 `psycopg 3.3.6`、`djangorestframework 3.18.3`；在表下加一行註記「版本於 2026-10-21 對 PyPI／npm registry 實際查核；升降級須另開 AD」；並新增規則「後端與前端依賴以 `requirements.txt` 與 `package-lock.json` 鎖定，lockfile 必須入版控，CI 安裝以 lockfile 為準」（與 H7 的強制機制一併落地）。

### 3.3 Medium（15）

| # | 位置 | 問題 | 修法 |
| --- | --- | --- | --- |
| M1 | AD-18、AD-3 | 未禁止操作人員由 client 傳入；AD-18 只說「保存操作人員」 | AD-18 追加「操作人員一律取自 `request.user`，不接受任何請求欄位傳入；use case 函式以 actor 參數注入並由 view 傳入 `request.user`」 |
| M2 | Map R5（AD-2,3,14） | 查詢語意未定：精確名稱優先、部分關鍵字最小長度、空結果不是錯誤、無庫存時的表示 | AD-07／新增 AD 明定查詢語意：排序＝完全相同 > 前綴 > 包含，空結果回 `200` 空陣列（不是錯誤包絡），分頁與過濾參數名固定 |
| M3 | AD-3、AD-12 | 異動正負號約定（入庫正／移出領用銷貨負）與「移轉、調貨各產生兩筆」的產生時點未明文 | AD-12 追加「`STOCK_MOVEMENT.qty` 帶正負號，規則為入庫／調入為正、領用／移出／調入對應之移出／銷貨為負；同倉移轉與跨倉調貨各自在**同一個 atomic 區塊**內產生移出與移入兩筆紀錄」 |
| M4 | AD-8、AD-11（R9／R11） | 「缺單價或數量不可儲存」未由 Rule 承載；「入庫必須指定批次、單價取自批次且入庫端不得輸入」未明文；批次數量與實際入庫量的關係（批次可先建尚未到貨）未定 | AD-8／AD-11 追加：「批次建立時必填單價與數量，缺任一拒儲；入庫 use case 必須引用既有批次且單價只讀自批次，入庫請求不得攜帶單價；允許同一批次多次入庫，累計入庫量不得超過批次數量」 |
| M5 | Map R10、AD-8 | 位置代碼格式（PRD §8.2 第 6 項為暫定值 `A-03`）未定案，而 AD-8 假定編碼已定 | 與 H8 併案：列為 Open Question，暫定 `A-03`，並在 AD-20 明定「格式一旦確認即以 DB CHECK 或格式驗證器落實，變更需 migration」 |
| M6 | Map R8（AD-2,3,14） | R8「低於水位清單」規則本身無 AD；且水位欄位在 catalog、規則在 stock，跨 app 寫入歸屬與 AD-2 的「寫入走對方 service」關係未定義（形成寫入方向不明） | 新增 AD-25 — 補貨水位：規則寫明「水位為商品層級整數欄位，預設 0 代表不列入清單；水位欄位歸 `catalog`，寫入水位只能呼叫 `catalog` 的 service（AD-2），低於水位判定為 stock 側的唯讀查詢（跨倉彙總或單倉口徑需明定）；補貨入庫後重新計算，庫存 ≥ 水位即離開清單」 |
| M7 | AD-4（R13／R14） | 「移轉限於同一倉庫」與「一張調貨單只對應一個目標倉庫、免審批即時生效」未明文 | AD-4 追加：「移轉 use case 必須驗證來源與目標 `Location` 屬於同一 `Warehouse`，否則拒絕；調貨單一單一目標倉庫，建立即生效不需審批」 |
| M8 | Map R17（AD-7,9） | 一階不疊加、0–100% 範圍拒儲、百分比表示法（10% 記為 0.1）未明文 | AD-9 追加：「折扣率為 Decimal(5,4)，以小數表示（10% 記為 0.1），值域 0 ≤ r ≤ 1，越界拒儲；一張銷貨單僅一階折扣，不與行內折扣疊加；折後金額 = 原價合計 ×（1 − r)，以 ROUND_HALF_UP 捨入至小數兩位」 |
| M9 | Map R18（AD-9,11） | 「無入庫成本紀錄時顯示『成本未設定』而非 0」的 null 語意未規則化；建議售價／預計毛利（商品層級）在 catalog，map 只寫「catalog（批次成本）」 | AD-11 追加：「成本為 nullable；無任何可消耗批次時成本回傳 null 並在 UI 顯示『成本未設定』，不得以 0 代替；建議售價與預計毛利為 catalog 的商品層級欄位，由 sales 唯讀引用」 |
| M10 | Map R19（AD-3,12,18） | 「依日期或銷貨單號查詢」的查詢契約未定；銷貨單號格式未定義（AD-8 只定義商品與批次編號） | AD-8 追加銷貨單號格式（如 `SO-YYYYMMDD-序號`）與產生方式；AD-07 或新增查詢契約段落固定日期區間與單號查詢的參數名與回應形狀 |
| M11 | Map R20（AD-5,6） | 「停用帳號不可登入、既有紀錄保留」未明文；AD-12 的 `is_active` 軟刪除適用範圍未列帳號 | AD-5 追加：「帳號停用以 `is_active=False` 表達，停用帳號登入一律拒絕且回應與密碼錯誤相同；停用不影響既有異動與銷貨紀錄」；AD-12 明列 `is_active` 適用對象＝帳號／供應商／商品／倉庫／位置 |
| M12 | AD-12 | AD-12 只把供應商、商品列為可軟刪的設定類，但 addendum §D 與 initiative Boundaries 明列**批次**為交易類「不刪除、不軟刪除」。AD-12 未提批次，規則可被讀成批次也可軟刪 | AD-12 明列：「可軟刪除對象僅限帳號、供應商、商品、倉庫、庫存位置；批次、庫存異動、銷貨單與銷貨紀錄一律不得刪除或軟刪除」 |
| M13 | Deferred 第 252 行、AD-14 | 效能基準（1,000 商品／10,000 異動／清單與明細 2 秒內）是 ticket Constraint C5 與 PRD §4.6 的驗收條件，但 spine 無任何 AD，Deferred 以「靠索引即可達成」帶過，且未指定必要索引（商品名稱、批次號、warehouse、item、movement 日期）與種子資料規模 | 新增 AD-26 — 查詢效能基準：規則寫明「必須提供固定種子資料集（1,000 商品／10,000 異動）與索引規格（`Item.name`、`Batch.batch_no`、`StockMovement.(item, created_at)`、`StockLevel.(item, location)`）；以 pytest 標記 `perf` 的測試斷言清單與明細查詢 < 2 秒」 |
| M14 | AD-15、AD-6（R 相關 Constraints C1／C2） | ticket Constraint C1「所有資料存取不得以字串拼接 SQL」在 spine 沒有對應 Rule；AD-15 只管憑證。密碼雜湊演算法也未指定（AD-6 只說 session+CSRF） | AD-15 追加：「所有 SQL／ORM 查詢一律經 ORM 或參數化查詢，禁止字串拼接 SQL（可用架構測試或 lint 檢查）；使用者密碼使用 Django 預設 PBKDF2 雜湊，不得自訂為可逆或無 salt」 |
| M15 | AD-18、AD-16 | 應用日誌只規定內容，未定等級／輸出位置／保留期；AD-16 說要防「前端與後端版本不一致」卻無任何規則（無 lockfile、無相容性矩陣） | AD-18 追加：「日誌輸出至 stderr、格式含 level/time/request id/actor/use case，保留期至少涵蓋一次課程驗證週期；密碼與憑證永不入日誌（已述）」；配合 H9 補 lockfile 規則 |

### 3.4 Low（5）

| # | 位置 | 問題 | 修法 |
| --- | --- | --- | --- |
| L1 | Deferred「備份與復原」 | 對課業可接受，但與 AD-18「庫存異動永久保存」及 SM-3「1 分鐘內可追溯」存在張力：本機資料庫無備份即無任何遺失復原能力 | 於 Deferred 補一句「v1 接受本機資料庫遺失風險；課程驗收前需匯出一份 SQL 備份作為最低限度保全」 |
| L2 | 缺少決策紀錄 | addendum §F 的「ER 圖工具（dbdiagram.io）」在 spine 中未列入 Deferred、未列入已決事項，實際上 spine 以 Mermaid ERD 呈現 | 於 spine 補一列「已決：ER 圖以 Mermaid 描述於本 spine，dbdiagram.io 不採用」 |
| L3 | 全文 | spine 未對照 addendum §F「明確擱置的技術決定」清單逐項標記由誰解決（後端框架、資料庫、架構模式、ER 工具、成本基準） | 於 spine 末尾加一張「addendum §F 對照表」逐行標示「本 spine 已解決：AD-x」 |
| L4 | Done when | initiative 的 Done when 1–5 沒有對應到可驗證的測試／AD 條目 | 於 AD-14 追加一張對照表，把 Done when 1–5 對應到具體 pytest 測試名稱或 AD 條目 |
| L5 | Deferred「容器化、CI/CD」 | 版本控制與分支策略完全未提（CI 已 deferred，但版控約定不應隨之留白） | 於 Consistency Conventions 或 AD-14 補「採 trunk-based、main 為保護分支、PR 需通過 AD-24 檢查與 pytest 全綠」 |

---

## 4. 建議修訂優先序

1. **先補規則（會改變下游實作）**：H1（登入鎖定）、H2（唯一鍵）、H3（建議調貨來源）、H4（領用用途與毛利）、H5（銷貨單狀態機）、M6（補貨水位歸屬）—— 這六條都是「兩個 unit 會各自拍板」的分歧點，應在 story 拆解前定案。
2. **再補 envelope**：H6（正式環境與秘密管理）、H7（架構約束的自動化強制）、H8（Open Questions 章節）—— 直接對應 checklist 的「每個維度都必須被決定／延後／列為開放問題」。
3. **再修技術事實**：H9（psycopg 3.3.7 不存在、DRF 3.17.1 不支援 Django 6.1）。
4. **最後補一致性**：Medium 15 項與 Low 5 項。

修訂完成後建議將 spine `status` 由 `draft` 改為 `ratified`，並為 AD-19～AD-26 補上 `Binds`（對應的 R 與 ticket Constraint）與 `Prevents`（具體說明被阻止的分歧）。

---

## 5. 保留的優點（供修訂時保留）

- 分層單體 + 明確 service 層作為領域寫入唯一邊界，與 PRD 的交易完整性要求高度對齊。
- 單向依賴 `sales → stock → catalog` 的規則表達清晰，是本 spine 最強的防分歧設計。
- AD-9（數值型別與捨入）、AD-11（FIFO 且不存彙總成本）、AD-12（僅追加 + 軟刪除範圍）、AD-17（單一錯誤包絡）四條規則具體、可驗證，能真正阻止對帳不平與錯誤形狀分歧。
- 與既有環境（`AILearn` 單庫、`pgpass.conf`／`PGPASSFILE`、無明文密碼）完全相容，符合 addendum §C、§D，未牴觸 brownfield。
- Deferred 清單整體安全，未出現「把會造成單位分歧的事項丟進 Deferred」的越界情形。
