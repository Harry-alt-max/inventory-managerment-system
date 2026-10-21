# 對抗式審查 — Architecture Spine「庫存管理系統」

- 審查對象：`_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`（status: draft）
- 審查視角：把 spine 當成對手。四個 epic（E1 accounts／E2 catalog／E3 stock／E4 sales）視為可能由不同 agent 同時實作的 unit；逐一檢查「兩個 unit 各自字面遵守每一條 AD，卻建出互不相容的東西」的情形。
- 產出方式：僅閱讀 spine、initiative、PRD、addendum 與四份 epic ticket；未修改任何被審文件。
- 嚴重度：**S1 = 會讓帳面對不上／重複扣減／毛利錯算**；**S2 = 會讓串接失敗但不會直接錯帳**；**S3 = 規範不清、執行時才發現**。

---

## 0. 結論

spine 的方向規則與「寫入只走 service」骨架是對的，但**它只規定了「誰不能寫什麼」，沒有規定「事實住在哪一個表、欄位、排序鍵與介面簽章」**。因此多組 S1 級分歧是「字面合規」的必然結果，而非違規。共找到 **14 組可建構的不相容分歧**（S1 × 6、S2 × 5、S3 × 3）、**11 條 Rule 不可強制或寫法有誤**、以及 **6 條只存在於散文而未被 AD 綁定的規則**。

最關鍵的一句話總結：**這份 spine 讓 E3 與 E4 可以各自做出「合規但不同」的庫存真相。**

---

## 1. 分歧清單（總表）

| # | 涉及 unit | 不相容結果一句話 | 嚴重度 |
| --- | --- | --- | --- |
| D1 | E3 × E4 | 銷貨事實被寫三處（銷貨行／銷貨紀錄／庫存異動），沖銷只補其中一處 | S1 |
| D2 | E3 × E4 | 「現有庫存」是 STOCK_LEVEL 欄位還是 STOCK_MOVEMENT 彙總，兩邊各選一邊 | S1 |
| D3 | E3 × E4 | 銷貨行沒有位置欄位 → 扣減位置由誰挑；可售量與實際扣減來源不一致 | S1 |
| D4 | E2 × E3 × E4 | 批次消耗明細的形狀與 FIFO 排序鍵不同 → 成本與毛利率不一致 | S1 |
| D5 | E3 × E4 | stock 不得 FK 到 sales，導致「每筆銷貨異動必須有銷貨行」無法在 DB 層強制 | S1 |
| D6 | E3 × E4 | 調貨單住在 stock 還是 sales；跨倉異動對應到哪一張單 | S1 |
| D7 | E1 × E3 × E4 | actor 取得方式（thread-local vs 顯式參數）與 accounts 依賴方向未定義 | S1 |
| D8 | E1 × E3 × E4 | permission codename 詞彙不同 → 合法使用者被 403 | S2 |
| D9 | E2 × E3 × E4 | 銷貨單號／調貨單號格式未定義；PO 序號的產生方式未定 | S2 |
| D10 | E2 × E3 | 水位、批次數量語意等欄位出現「兩個 home」 | S2 |
| D11 | E1 × E3 × E4 | 用途／角色／折扣率的值域與常數來源不同 → 同一輸入兩種判定 | S2 |
| D12 | E1 × E3 × E4 | 同一 schema 平行跑 `makemigrations` → conflicting migrations，建不起來 | S2 |
| D13 | E3 × E4 | 清單口徑不一致（現存量 vs 可用量）、「成本未設定」的判定依據不同 | S2 |
| D14 | E3 × E4 | 可用量檢查與扣減分屬不同交易、沒有列鎖 → 超賣導致負庫存 | S1 |

---

## 2. 各分歧詳細說明

### D1 — 銷貨事實被寫成三份，沖銷時三份不同步（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-3（寫入只經 use case）、AD-12（交易類資料僅追加、取消銷貨以反向沖銷紀錄表達）、AD-4（銷售用途扣減唯一入口）、AD-9（金額型別）
- **建構過程**
  - E4 agent：銷貨送出時寫 `SALES_ORDER_LINE`（數量、金額、批次）＋ `SALES_RECORD`（操作人員、日期、數量、金額、批次）。
  - E3 agent：庫存異動 `STOCK_MOVEMENT`（用途＝銷貨、數量、批次、操作人員）＋ 更新 `STOCK_LEVEL`。
  - 兩邊都完全符合 AD-3／AD-12：都是 service use case、都只 append、沖銷用 append。
- **不相容結果**：同一筆交易在三處各存一份數量與批次。**沖銷時**，E3 agent 只 append 一筆 `STOCK_MOVEMENT(SALE_REVERSAL)` 並回加 `STOCK_LEVEL`；E4 agent 只 append 一筆 `SALES_RECORD(REVERSAL)` 並把銷貨行標為已沖銷（但 AD-12 又不允許 update 銷貨紀錄 → 可能改標銷貨行的狀態欄，變相違反僅追加）。結果：銷貨紀錄顯示「銷 5 沖 0」、庫存異動顯示「銷 5 沖 5」、銷貨行顯示「已沖銷」，三份對不上；AD-14 的帳面等式只涵蓋異動表，看不出銷貨紀錄與異動已經脫鉤。毛利查核（會計角色，UJ-4）會拿到錯誤數字。
- **具體修法（新增 AD-29 — 事實的唯一 home 與欄位權威）**：
  > **Rule**：同一業務事實只允許一個 home 表，每個欄位只允許一個權威來源，不得跨表複製：
  > - 銷貨行（商品、數量、**庫存位置**、折扣、折後金額）→ `sales` 擁有
  > - 批次消耗明細（銷貨行 × 批次 × 數量 × 單價）→ `sales` 擁有（見 AD-22）
  > - 成本與毛利（派生值）→ 由銷貨行與消耗明細**即時計算**，不落庫（符合 AD-11）
  > - 庫存數量事實 → `stock.STOCK_MOVEMENT` 唯一擁有
  > - 庫存現況 → `stock.STOCK_LEVEL` 唯一擁有
  > - 沖銷必須三處**在同一個 `transaction.atomic()` 內**以 append 產生反向列；任一處失敗整筆回滾。
  > - 禁止在 `STOCK_MOVEMENT` 上重複存放金額；禁止在 `SALES_RECORD` 上重複存放批次消耗明細。

---

### D2 — 「現有庫存」是欄位還是彙總，兩邊各選一邊（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-2（sales 可讀 stock）、AD-3（寫入只經 use case）、AD-12（異動僅追加）
- **建構過程**
  - E3 agent：`STOCK_LEVEL(item, location, quantity)` 為現況欄位，每次 use case 同步 `F()` 更新；另提供 `available_by_item()` 查詢。
  - E4 agent：R15「各倉可用量」自己用 `Sum(STOCK_MOVEMENT.quantity)` 對 `stock` 公開模型彙總（AD-2 允許 sales→stock 讀取），理由是「AD-11 禁止彙總成本、我就用彙總現況」，或為了避開 STOCK_LEVEL 尚未建好的依賴（E4 的 epic `after` 順序雖在 E3 之後，但 agent 未必知道 STOCK_LEVEL 的存在）。
- **不相容結果**：同一次查詢回傳兩個數字。E4 的彙總在有「同倉移轉」時會錯（移出 −n、移入 +n 同商品不同位置，彙總與位置加總口徑不同），且忽略 `STOCK_LEVEL` 的「不為負」守衛；若任一 use case 漏寫一條異動（例如草稿銷貨保留、或沖銷只加異動沒加彙總口徑的相反數），兩個數字永久分歧。更糟：AD-14 的帳面等式以異動表為準、UI 以 `STOCK_LEVEL` 為準 → 「帳面等式 = 0」通過但畫面數字錯。
- **具體修法（新增 AD-20 — 庫存現況的唯一真相）**：
  > **Rule**：`stock.STOCK_LEVEL` 是「商品 × 位置」現有庫存的**唯一真相**，由 stock app 唯一擁有，並且**必須與同一交易內的 `STOCK_MOVEMENT` 一起更新**。任何 app 不得以「即時彙總 `STOCK_MOVEMENT`」作為對外的現況數字；跨 app 的現況讀取只能呼叫 stock app 明列的公開查詢 use case（AD-19）。`STOCK_LEVEL` 與 `STOCK_MOVEMENT` 的差額必須為 0（由 AD-14 的測試強制）。

---

### D3 — 銷貨行沒有位置欄位，扣減位置由誰挑（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-2（寫入他人資料走對方 service）、AD-4（庫存數量不得為負）、AD-7（API 契約固定）、AD-9
- **建構過程**
  - E4 agent：FR-16 明文只要求「商品、數量」，銷貨單**不含位置**；銷貨行的 `location` 是可空的，扣減時呼叫 `stock.deduct(item, qty)`，讓 stock 決定從哪個位置扣。
  - E3 agent：`STOCK_LEVEL` 的 key 是 (item, location)（spine ERD 明列），`deduct()` 必須挑一個位置。挑法沒有 AD 規定 → E3 挑「數量最多的位置」，另一個 E3 agent 挑「最早入庫的位置」，或挑「同倉第一個位置」。
- **不相容結果**：R15（FR-15）要求銷售看到「各倉可用量」並由 E4 渲染，銷售據此告知客戶「B 倉有 10 件可出」；實際扣減卻發生在 A 倉 → 客戶在 B 倉提貨時無貨，而畫面仍顯示 B 倉有貨。更硬的衝突：FIFO 成本的計算基礎是「該位置的批次序列」，位置選不同 → 成本不同 → 同一張銷貨單由不同 agent 實作會得到不同毛利。AD-9 的金額精度再怎麼嚴格也救不了這個。
- **具體修法（新增 AD-21 — 銷貨扣減契約：位置、批次、交易與鎖）**：
  > **Rule**：銷貨行**必須**攜帶庫存位置（`location` 非空，API 契約 AD-7 同步更新）；若由 stock 代為挑選位置，stock 的扣減 use case 必須回傳**實際扣減位置**並由 sales 存回銷貨行與消耗明細。可用量檢查與扣減必須在**同一個 `transaction.atomic()`** 內完成，並對 `STOCK_LEVEL` 該列 `SELECT ... FOR UPDATE`（或等效樂觀鎖）後**重驗**；禁止「先查後改」的跨交易檢查。stock 的扣減 use case 回傳的「位置＋批次消耗明細」是銷貨紀錄與毛利的**唯一**來源。

---

### D4 — 批次消耗明細的形狀與 FIFO 排序鍵不一致（S1）

- **兩個 unit**：E2（catalog）與 E3（stock）、E4（sales）
- **各自遵守的 AD**：AD-11（FIFO、批次原始資料不可被彙總取代）、AD-13（跨 app FK 只指向被依賴 app 的公開模型）、AD-2
- **建構過程**
  - spine ERD 只畫 `BATCH ||--o{ SALES_ORDER_LINE : consumed_from`，即「一條銷貨行對一個批次」。
  - E4 agent：一行賣 5 件、批次 A 只剩 3 件 → 拆成兩條銷貨行（3＋2），或（更常見）在銷貨行上加 `consumed_batch` FK。
  - E3 agent（stock 側 FIFO 引擎）：一次扣減跨批次，必須記錄多筆 `(movement, batch, qty)` → 需要一張連結表 `STOCK_MOVEMENT_BATCH`。
  - FIFO 排序鍵沒有 AD：E4 agent 用 `Batch.created_at`（批次可先於到貨建立，PRD FR-9）；E3 agent 用入庫異動時間（真正的 FIFO 順序）。
- **不相容結果**：**(a)** 一行跨批次的銷貨在 sales 端無法逐批次記錄成本（連結表缺位）→ 毛利只算到第一個批次或用平均單價 → 與 AD-11 的 FIFO 定義不符。**(b)** 排序鍵不同 → 批次 A（先建後到）與批次 B（先到後建）誰先被消耗不同 → 成本不同 → 同一筆交易在兩 agent 實作下毛利不一致，會計核對（UJ-4）失敗。**(c)** 移轉／領用若不帶批次，`STOCK_LEVEL` 是 (item, location) 而異動帶批次 → 批次層級的可用量無處可算，E4 的 FIFO 只能瞎猜。
- **具體修法（新增 AD-22 — 批次消耗明細與 FIFO 排序鍵）**：
  > **Rule**：FIFO 排序鍵**固定**為「該庫存位置上，入庫類 `STOCK_MOVEMENT` 的發生時間」，不得使用批次建立時間或採購日期。批次消耗明細（`sales` app 擁有：`SALES_LINE × BATCH × qty × unit_price`，跨 app FK 只指向 `stock` 的公開模型）**必須持久化**，禁止只在記憶體計算或只留單一批次欄位。每筆庫存異動（含移轉、領用、調出／調入、沖銷）**必填批次**；移出與移入必須是同一批次。

---

### D5 — stock 不能 FK 到 sales，「每筆銷貨異動必有銷貨行」無法強制（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-2（`stock` 不得呼叫 `sales`）、AD-13（跨 app FK 只指向被依賴 app 的公開模型）、AD-4（銷售扣減唯一入口）
- **建構過程**：E3 agent 想在 `STOCK_MOVEMENT` 上加 `sales_order_line_id` 欄位以落實「銷售用途的扣減必須來自銷貨單」，但 AD-2／AD-13 禁止 stock → sales 的 FK；於是 E3 agent 改放一個**可空的字串欄位** `sale_ref`（無 FK、無約束），或干脆不記。E4 agent 端則在 `SALES_LINE` 上加 `movement_id` FK（sales → stock，方向合法）。
- **不相容結果**：**兩個 owner 事實同一件事**——「這筆異動屬於哪張銷貨單」。E3 端無約束的 `sale_ref` 可為任意字串、可指向不存在的單號；E4 端 FK 保真。兩份都對外顯示時，帳面等式（AD-14）檢查異動，銷貨紀錄查詢（R19）查 sales 表 → 同一筆銷貨可能「異動有、銷貨紀錄無」（E4 的 use case 中途失敗但 E3 已 commit，或 E3 自行產生用途＝銷貨的異動）。
- **具體修法（新增 AD-24 — 銷售用途扣減的雙向可驗證 + 補 AD-2 的方向白名單）**：
  > **Rule**：庫存端**不得**持有指向 sales 的 FK。銷貨參考改由 sales 端維護的連結表 `SALES_LINE_MOVEMENT(sales_line_id, movement_id, qty)` 表達（sales → stock 方向合法）。扣減 use case 必須接受「銷貨行參考」作為必填參數；stock 端**不得接受**無銷貨行參考的銷售用途扣減。在同一交易內必須檢查「每一筆用途＝銷貨的 `STOCK_MOVEMENT` 皆被某 `SALES_LINE_MOVEMENT` 引用」且「每一筆已送出銷貨行皆有對應引用」，否則整筆回滾。AD-2 的允許清單補上 `sales|stock → accounts/core` 的讀取（見 D7）。

---

### D6 — 調貨單住在 stock 還是 sales；跨倉異動對應哪張單（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-2（寫入他人資料走對方 service）、AD-4（跨倉庫存變動必須帶有調貨單）、AD-13
- **建構過程**：PRD FR-14 說「銷售與倉管人員可建立調貨單」；spine 只說「跨倉變動必須帶有調貨單」，**沒有說調貨單這張表住在哪個 app**。
  - E4 agent（讀到 FR-14 有自己一份）：在 sales 建 `TRANSFER_REQUEST`，由銷售端建立「待調貨」並自行記錄來源/目標倉庫。
  - E3 agent：在 stock 建 `TRANSFER_ORDER` 並在移出／移入異動上放 `transfer_order_id`。
  - 兩者都完全合規（各自寫自己的 model，跨 app 只走 service）。
- **不相容結果**：**跨倉異動對應到 E3 的 `TRANSFER_ORDER` 編號，但銷售端畫面顯示的是 E4 的 `TRANSFER_REQUEST` 編號** → UJ-3 的「改為建立調貨單，改由 B 倉調貨後再出貨」流程在兩邊對不起來；AD-14 的測試「任何跨倉庫存變動都對應到一張調貨單」只對得上 E3 那一張，銷售端那張成為無主單據。兩個編號命名空間還可能撞號。
- **具體修法（新增 AD-25 — 調貨單的 home 與呼叫方式）**：
  > **Rule**：調貨單（`TRANSFER_ORDER`）及其移出／移入異動**唯一住在 `stock` app**。sales 不得建立調貨相關的領域單據；sales 若要保存「此單待調貨」的狀態，只能存放 **stock 頒發的調貨單號字串參考**。跨倉調貨必須是**同步 service 呼叫**（非佇列、非共享表）；同一張調貨單只對應一個目標倉庫，且移出與移入必須在同一交易內成對寫入。

---

### D7 — actor 傳遞契約未定義 + accounts 不在依賴方向白名單（S1）

- **兩個 unit**：E1（accounts）、E3（stock）、E4（sales）
- **各自遵守的 AD**：AD-2（允許 `stock→catalog`、`sales→catalog`、`sales→stock` 讀取）、AD-18（永久保存操作人員）、AD-3
- **建構過程**：initiative Boundaries 說「操作人員帶入機制由 E1 建立，E3／E4 沿用」，但 spine 沒有定義它的介面。
  - E3 agent：`from core.actor import get_current_actor`（thread-local，由 middleware 塞入）→ use case 不接受 actor 參數。
  - E4 agent：`sales.services.submit_order(actor=user, lines=[...])` 顯式傳 actor，並在呼叫 stock service 時把 actor 一起傳過去。
  - 問題在於 **AD-2 的允許讀取清單不含 accounts／core**：E4 若要寫入 actor 的帳號代號快照在 `SALES_ORDER` 上，它可以讀 `accounts.User` 嗎？依 AD-2 的字面（只允許三種讀取），不行；依 AD-18（要保存操作人員），又必須寫到帳號代號。E3 agent 更常見的作法是把 `actor_id` 直接做成指向 `accounts.User` 的 FK——這會讓 stock → accounts 依賴，超出 AD-2 白名單，但 AD-2 沒有禁止 accounts 方向的讀取，只是沒列。
- **不相容結果**：(a) **actor 取不到**：E4 呼叫 E3 的 service 時（跨 app 呼叫通常不在 request 情境內，例如由銷貨 use case 內部觸發扣減），E3 的 thread-local 為空 → 寫入 `actor=None` → 違反 AD-18 與 R3「非空操作人員」；或者 E3 丟錯 → 銷貨整筆失敗。(b) **actor 取得方式不一致**：E3 記帳號代號字串、E4 記 `accounts.User` FK → 停用／刪除帳號時 FK cascade 抹掉既有紀錄，直接違反 R20「既有紀錄保留」。(c) **依賴方向分歧**：一個 agent 認為 accounts 可依賴，另一個認為不可依賴，兩邊的 import 圖不一致。
- **具體修法（新增 AD-26 — Actor 傳遞契約 + 補 AD-2 白名單）**：
  > **Rule**：所有 use case 的**第一個參數為 `Actor`**（`core` 定義的值物件：`username`、`role`、`display_name` 快照，不可為 null），由呼叫端**顯式傳入**；禁止從 thread-local、request、session 隱式取得；`core` 提供測試用建構子。異動與銷貨紀錄保存的是 **actor 的不可變快照**（帳號代號字串），**不得以 FK 指向 `accounts.User`**，以確保停用帳號不影響既有紀錄。任何 app 讀取 `core` 與 `accounts` 的**公開**（帳號代號、角色、是否啟用）是允許的（補入 AD-2 允許清單：`{any} → accounts/core` 唯讀）；`accounts` 不得依賴其他領域 app。

---

### D8 — permission codename 詞彙不同，合法使用者被 403（S2）

- **兩個 unit**：E1（accounts／core/permissions.py）與 E3（stock）、E4（sales）
- **各自遵守的 AD**：AD-5（permission codename 由 `core/permissions.py` 集中宣告、view 宣告所需權限、越權 403、會計唯讀）
- **建構過程**：AD-5 要求集中宣告，但**沒有規定命名規則，也沒有規定誰先寫**。
  - E1 agent 宣告：`stock.add_stock`、`stock.receive`、`sales.make_sale`、`sales.view_margin`。
  - E3 agent 在自己的 view 宣告 `required_permissions = ["stock.receive_stock"]`（自認合理的命名）。
  - 兩邊都符合 AD-5（「由 core/permissions.py 集中宣告」——E1 的確集中宣告了；E3 的 view 也的確宣告了所需權限）。
- **不相容結果**：倉管呼叫入庫 API 得到 403（權限碼不匹配），但 R11 應可操作 → Done-when 失敗；反之，若 E3 為了「能跑」而在自己的 view 加 `has_permission` 自訂檢查而沒有用 DRF 的 `required_permissions`，則 AD-5 的「集中宣告」形同虛設，審計與測試都要改寫。會計唯讀也一樣：E4 的毛利 view 若同時掛了 `sales.make_sale`，會計就會被擋在查核之外，UJ-4 直接失敗。
- **具體修法（收緊 AD-5）**：
  > **Rule（補）**：permission codename 一律為 `<app>.<resource>.<action>`（`action ∈ {add, list, retrieve, change, approve}`）；`core/permissions.py` 是唯一宣告處，且**必須在消費該權限的 view 之前存在**；view 一律使用 DRF `required_permissions`，禁止自訂 `has_permission` 分岔。會計角色不得被授予任何 `add`/`change` 權限，其「查看銷貨紀錄與毛利」需另給唯讀 codename（如 `sales.view_margin`、`sales.view_sales_record`）。新增/變更權限 codename 時，必須同步更新 `core/permissions.py` 與一份 codename 清單文件，並有測試驗證每個 codename 至少被一個 view 宣告（避免孤兒權限）。

---

### D9 — 銷貨單號／調貨單號未定義；PO 序號的產生方式未定（S2）

- **兩個 unit**：E2（catalog）、E3（stock）、E4（sales）
- **各自遵守的 AD**：AD-8（業務編號與內部主鍵分離；`INV-` + 6 碼；`PO-YYYYMMDD-序號`，DB sequence 產生、同日全域遞增）
- **建構過程**
  - AD-8 **完全沒有提到銷貨單號與調貨單號**，但 R19 要求「可依銷貨單號查詢」、R6 要求異動可對應調貨單。E4 agent 自創 `SO-20261021-001`；E3 agent 自創 `TR-0001` 或 `TO-20261021-1`。兩邊都沒有違反 AD-8（AD-8 只列了兩種編號）。
  - AD-8 要求「由 DB sequence 產生」且「同一日內全域遞增」——PostgreSQL 的 sequence 是**全域遞增**，要「同日序號」就必須每日重置或另建 counter 表。E2 agent 用「每日重設 sequence」；另一個 E2 agent 用 `(date, seq)` counter 表 + `SELECT ... FOR UPDATE`；還有人用 `max(seq)+1`（併發下會撞號）。
- **不相容結果**：(a) 銷貨單號與調貨單號格式兩套，跨 app 查詢與前端顯示不一致；外部若要引用單號，無共同格式。(b) PO 序號在兩種實作下可能撞號（`max()+1` + 併發）或跳號（每日重置 sequence 在午夜有競態），R9「同日流水號不重複」在測試中可能 flaky 失敗。
- **具體修法（收緊 AD-8 + 新增 AD-27）**：
  > **Rule（補）**：所有對外業務編號一覽固定：商品 `INV-` + 6 碼（E2 分配）、採購批次 `PO-YYYYMMDD-` + 4 碼（E2 分配）、銷貨單 `SO-YYYYMMDD-` + 4 碼（E4 分配）、調貨單 `TO-YYYYMMDD-` + 4 碼（E3 分配）。序號一律以 `(business_date, seq)` counter 表實作，對該列 `SELECT ... FOR UPDATE` 取號後遞增，並以 `(business_date, seq)` 唯一約束兜底；**禁止** `max()+1`、禁止跨日重設 sequence、禁止應用層計數。編號建立後不可修改。

---

### D10 — 欄位出現「兩個 home」（水位、批次數量語意）（S2）

- **兩個 unit**：E2（catalog）與 E3（stock）
- **各自遵守的 AD**：AD-1（app 邊界）、AD-2（寫入他人資料走對方 service）、AD-8
- **建構過程**
  - 水位：epic ticket 已寫「商品主檔預留可空的水位欄位」（E2）＋「待補貨清單規則」（E3）。E2 agent 在 `Item.reorder_level` 放水位；E3 agent 為了讓清單查詢不必跨 app 讀，在 stock 建 `ItemReorderLevel(item, level)`。兩者都沒寫入對方 model → 不違反 AD-2。
  - 批次數量語意：E2 的 `Batch.quantity` 是「採購數量」還是「尚可用數量」？PRD FR-9 只說批次有數量。E2 agent 視為採購數量（不變）；E3 agent 視為「可入庫／可消耗餘額」，在入庫或銷貨時回寫 `Batch.quantity`——但那是寫入 catalog 的 model，AD-2 禁止，於是 E3 改為呼叫 catalog 的 service 更新（此時 catalog 有兩個 service 版本）。
- **不相容結果**：(a) 使用者在 E2 設定水位 50、在 E3 清單看到缺口依另一個值算 → 待補貨清單錯（UJ-2）。(b) 批次數量若被兩處維護，`STOCK_LEVEL`（現況）與 `Batch.quantity`（批次餘額）成為**兩個庫存真相**，FIFO 可用批次數量不可信 → D4 的成本錯算連鎖發生。
- **具體修法（收緊 AD-28 — 欄位 home 唯一性表）**：
  > **Rule（補）**：下列欄位/home 唯一且不得在第二處建立同名或同義欄位：商品編號／水位／建議售價／預計毛利 → `catalog.Item`；批次採購單價與採購數量 → `catalog.Batch`（**不可變**，僅追加）；倉庫／位置 → `catalog`；庫存現況 → `stock.STOCK_LEVEL`；庫存異動 → `stock.STOCK_MOVEMENT`；待補貨清單規則與缺口計算 → `stock`；銷貨單／銷貨紀錄／批次消耗明細／毛利 → `sales`；actor 快照 → `core` 值物件。使用者設定水位必須呼叫 `catalog` 的公開 service（AD-19），`stock` 只讀不複製。

---

### D11 — 用途／角色／折扣率的值域與常數來源不同（S2）

- **兩個 unit**：E1（accounts）、E3（stock）、E4（sales）
- **各自遵守的 AD**：AD-4（領用用途不得為「銷貨」）、AD-5（角色固定四種）、AD-9（捨入與型別）、AD-17（領域例外集中）
- **建構過程**
  - 用途（purpose）列舉沒有 AD：E3 agent 在 `stock` 定義 `PURPOSES = {RECEIPT, ISSUE, CUSTOMER_SHIPMENT, TEMP_OUT, TRANSFER_OUT, TRANSFER_IN, SALE}`；E4 agent 需要的「銷售用途」在 stock 的列舉裡名稱不同（`SALE` vs `SALES` vs `銷貨`），E4 傳字串進去 → 不在 stock 的允許清單而被拒，或被寬鬆接受。
  - 折扣率：PRD FR-17 寫「10% 記為 0.1」但「不在 0～100% 範圍內時拒絕」——**PRD 本身矛盾**。E4 agent 存 `Decimal` 0~1；E1 agent 在共用驗證基線裡寫 0~100。同一個輸入 10 在兩邊一個是 1000% 折扣、一個是 10%。
  - 角色列舉（倉管／採購／銷售／會計）：AD-5 說固定四種但沒說 codename；E1 用 `WAREHOUSE/BUYER/SALES/ACCOUNTING`，E4 用 `warehouse/purchasing/sales/accounting` → 字串比對失敗。
- **不相容結果**：扣減被拒（合法銷貨送不出）、或折扣被接受為 1000 倍（金額為負、毛利失真）、或角色比對失效（越權通過或合法被擋）。
- **具體修法（新增 AD-30 — 封閉列舉與值域的單一事實來源）**：
  > **Rule**：所有跨 app 使用的列舉值（角色代碼、庫存用途／異動類型、領用用途、單據狀態）與數值範圍（折扣率、水位、數量）一律在 `core/constants.py` 宣告**單一事實來源**，各 app 只能 import，不得自訂字面值。折扣率以 `Decimal` 儲存，值域 **0 ≤ rate ≤ 1**（顯示為百分比），並統一 `ROUND_HALF_UP` 至小數兩位；範圍外的輸入由 `core` 的共用驗證函式拒絕（AD-17）。AD-11 的 FIFO 與 AD-4 的用途限制所依賴的列舉同樣納入此表。

---

### D12 — 同一 schema 平行跑 `makemigrations` → conflicting migrations（S2）

- **兩個 unit**：E1（schema 基線擁有者）、E3、E4
- **各自遵守的 AD**：AD-13（schema 變更唯一途徑為 Django migrations、migration 必須可從空庫一次跑完）、AD-15（單一 schema）
- **建構過程**：四個 app 是四個 agent 平行實作、四個分支。四個 agent 各自在**同一個** `AILearn` schema 上跑 `makemigrations` → 產生 4 個 `0N_*.py`（如 `0002_stocklevel.py`、`0002_salesorder.py`），merge 時 Django 報 **Conflicting migrations detected**；且 E4 的 FK 指向 stock 公開模型 → 需要 `dependencies = [('stock','0002_stocklevel')]`，若 stock 同時有 0002/0003，Django 會鎖定 leaf node。
- **不相容結果**：整合時 schema 建不起來，或必須人工手改 migration（違反 AD-13）；四個 agent 對同一個 `AILearn` 實測時互相污染對方的資料與 migration 歷史。
- **具體修法（收緊 AD-13）**：
  > **Rule（補）**：跨 app 的 FK 必須用 `swappable`／字串引用並在 `dependencies` 明確宣告被依賴 app 的 migration；**同一時間只有一個 app 執行 `makemigrations`／`migrate`**（migration 產生集中由 E1 統籌或在各分支完成後由單一整合者統一 `makemigrations`）。整合前必須通過 `makemigrations --check --dry-run`（無待產生 migration）與「從空庫一次跑完」的 CI 檢查。開發期允許各 agent 使用**獨立的測試資料庫**（AD-14 已要求），禁止對 `AILearn` 平行跑 migration。

---

### D13 — 清單口徑不一致與「成本未設定」判定依據不同（S2）

- **兩個 unit**：E3（stock）與 E4（sales），並牽涉 E2（catalog）
- **各自遵守的 AD**：AD-11、AD-2（讀取跨 app）
- **建構過程**
  - 現存量口徑：E3 的待補貨清單用「全倉現有庫存合計」；E4 的可售查詢用「各倉可用量」（可能扣除負數或以 FIFO 可用量計）→ 同一商品兩個數字（R8 與 R15 都要顯示「現有庫存」）。
  - 「成本未設定」：PRD FR-18 要求商品無入庫成本紀錄時顯示「成本未設定」而非 0，但**「有入庫成本紀錄」的定義沒有 AD**。E2 agent 實作為「存在 `Batch`」（批次可先於到貨建立）；E4 agent 實作為「存在入庫類 `STOCK_MOVEMENT`」。批次已建但未到貨的商品，前者顯示成本、後者顯示未設定。
  - FIFO 可用量：E3 若維護批次層級可用量（因 D4 需要），E4 若以 stock 公開的彙總查詢取數 → 口徑不同。
- **不相容結果**：UJ-2 的清單數字與 UJ-3 的可售數字不一致；FR-18 的「成本未設定」在兩處顯示不同 → 銷售報價與會計查核對不上。
- **具體修法（新增 AD-31 — 跨 app 查詢口徑與「有成本」定義）**：
  > **Rule**：「現有庫存」一律指 `STOCK_LEVEL` 的**跨位置合計**（AD-20），所有清單（待補貨清單、可售查詢、商品定位查詢）必須使用同一口徑，且由 stock app 提供**單一公開查詢 use case** 回傳（名稱、總量、各倉可用量、缺口）。「商品有入庫成本紀錄」定義為**存在至少一筆入庫類 `STOCK_MOVEMENT`**；不得以 `Batch` 存在或商品主檔上任何欄位判定。缺成本時 API 回傳明確的 `cost_status` 狀態而非 0（AD-7 錯誤／空值語意）。

---

### D14 — 可用量檢查與扣減分屬不同交易、沒有列鎖 → 負庫存（S1）

- **兩個 unit**：E3（stock）與 E4（sales）
- **各自遵守的 AD**：AD-3（`transaction.atomic()` 包住）、AD-4（庫存數量不得為負、超領整筆回滾）
- **建構過程**
  - E4 agent：銷貨送出流程為「先查可用量 → 顯示不足就回 409 → 再呼叫 stock 的扣減 use case」。查詢在**自己的** transaction／或根本不在 transaction 內；扣減在 stock 的 transaction 內。
  - E3 agent：stock 的 `deduct()` 內部檢查 `STOCK_LEVEL.quantity >= qty` 後扣減，但未對該列加鎖（`select_for_update`），且檢查與扣減之間夾著其他查詢。
- **不相容結果**：兩個 agent 都「以交易包住寫入」（AD-3 合規），但檢查與寫入不在同一交易 → 銷售與倉管同時操作同一位置時，兩個交易都讀到 quantity=5、各自扣 5 → `STOCK_LEVEL.quantity = -5`（AD-4 被違反，但責任落在哪一邊無法判定）。AD-4 的「超領時整筆回滾」在跨 app 的檢查情境下形同虛設，因為超額發生在 E3 之外。
- **具體修法（新增 AD-21 內含鎖要求 + 收緊 AD-4）**：
  > **Rule（AD-21）**：見上。**Rule（AD-4 補）**：任何「可用量檢查」必須在執行寫入的**同一個 transaction 內、對同一列加鎖後重驗**；API 層的預檢（回 409 提示不足）僅為友善提示，**不得**作為唯一的防護。`STOCK_LEVEL` 必須設 `CHECK (quantity >= 0)` 資料庫層約束作為最後一道防線（AD-15 同一 schema）。

---

## 3. Rule 不可強制／寫法有誤清單

| AD | 問題 | 建議 |
| --- | --- | --- |
| AD-14 | 帳面等式寫成「入庫 − 領用 − 調出 + 調入 − 銷貨 **= 0**」，但正確不變式是「等於 `STOCK_LEVEL.quantity`」。照字面實作會要求所有資料集淨額為 0，測試必失敗或被迫改寫 | 改寫為：`對每個 item：` Σ(有號數量) over STOCK_MOVEMENT == STOCK_LEVEL.quantity`，且每張調貨單的移出與移入淨額 == 0`。 |
| AD-12 | 「於 manager 層封鎖」不足：`bulk_update`、原始 SQL、`django-admin loaddata`、Django 內部 cascade 皆繞過；且 Django admin 預設提供刪除鍵 | 明寫封鎖清單（`update`/`delete`/`bulk_update`/`bulk_create`/`raw` 皆拋錯）、admin 唯讀、fixtures 只能走 append API，並以 DB 權限／觸發器作為補強選項。 |
| AD-12 | 「設定類資料（供應商、商品）以 `is_active` 軟刪除」未涵蓋倉庫／位置／帳號；倉庫停用後仍被 `STOCK_LEVEL` 參照 | 明確列舉可軟刪除的實體清單與不可軟刪除的清單；倉庫／位置停用必須先清空或改用 `is_active` 且不得刪除既有庫存列。 |
| AD-5 | 「由 `core/permissions.py` 集中宣告」無命名規則、無順序約束（見 D8） | 見 D8 修法。 |
| AD-8 | 「由 DB sequence 產生」與「同一日內全域遞增」在 PostgreSQL 上互斥（見 D9） | 見 D9 修法（counter 表 + 行鎖 + 唯一約束）。 |
| AD-9 | 未定義「捨入順序」與「折扣率型別／精度」；也未定義 `Decimal(12,2)` 對單價 × 數量溢位的處理 | 補：先以未捨入值計算、末端才 `ROUND_HALF_UP` 至 2 位；折扣率 `Decimal(5,4)`；數量 × 單價超出 `Decimal(12,2)` 時拋領域例外而非截斷。 |
| AD-11 | 「不得保存彙總成本欄位」只能靠 code review 強制；且未定義 FIFO 排序鍵與批次消耗明細形狀（見 D4） | 見 D4 修法；另可加 migration 檢查（欄位白名單）。 |
| AD-3 | 「只能在 `services.py` 的 use case 函式內完成」只約束了**檔名**，未禁止在 model 的 `save()` 覆寫、`custom manager` 或 signal 中寫入異動 | 補：異動／銷貨紀錄的建立只允許經由 `stock.services` / `sales.services` 匯出的 use case 函式；model 層不得覆寫 `save()` 寫入紀錄；signal 不得寫庫存。 |
| AD-1 | 「共用程式碼放 `core`」**未禁止 `core` 持有 model**；E3/E4 為共用跨 app 資料會把表塞進 `core`，形成第五個事實擁有者 | 新增 AD-32：`core` 不得包含任何 model（`core/models.py` 不得存在），core 僅含值物件、純函式、permissions、exceptions、money/time 工具。 |
| AD-2 | 允許讀取清單只有三條，**遺漏 accounts／core**；也未說明跨 app 的 FK 方向白名單與「不得反向依賴」的例外 | 補：允許 `any → core` 唯讀、`any → accounts` 唯讀（僅帳號代號／角色／啟用狀態）；跨 app FK 只允許 `sales → stock → catalog`。 |
| AD-7 | 「錯誤一律回應 `{code, detail, field_errors}`」未涵蓋**業務上合法的空值語意**（如 D13 的 `cost_status`、D3 的可售量為 0 的情況） | 補：業務空值用 `null` + 明確狀態欄位表達，不以錯誤包絡表示；`field_errors` 的鍵必須是請求欄位名。 |

---

## 4. 只存在於散文、未被 AD 綁定的規則（不可裁決）

以下規則在 spine 中具有約束力語氣，但不在任何 AD 的 `Rule` 內，因此兩個 agent 可以「都遵守 spine」而對它有不同理解：

1. **「方向規則：`sales → stock → catalog` 單向；`stock` 不得呼叫 `sales`；任何 app 不得寫入其他 app 的 model」**（Design Paradigm 段落）— 這是最重要的一條規則，卻不是 AD。建議提升為 **AD-2 的正式 Rule 條文**（目前 AD-2 只寫了允許清單，沒寫「任何 app 不得寫入其他 app 的 model」）。
2. **「`STOCK_LEVEL` 是『商品 × 位置』的現況（由異動累計），`STOCK_MOVEMENT` 是僅追加的異動明細，兩者不得互相取代」**（Structural Seed 段落）— 直接關聯 D2，應寫進 AD-20。
3. **「app 之間的 FK 只指向被依賴 app 的公開模型」**（AD-13 內，OK）但「公開模型」未定義（哪些 model 屬於公開？`stock.STOCK_LEVEL` 公開而 `stock.StockLevelInternal` 不公開？）。
4. **「跨 app 的讀取走被依賴 app 的公開模型」**（Design Paradigm 段落）— 未定義「公開」；D2 的彙總分歧正是「讀公開 model 但用錯讀法」的例子。應新增 **AD-19 公開介面清單**。
5. **Capability → Architecture Map 的歸屬**（例如 R18 = sales 計算 + catalog 批次成本）— 是資訊性表格，不是規則；agent 可以照它做，但也可以同時在 stock 實作一份 FIFO 而不違反任何 AD。
6. **Deferred 表**（例如「報表、快取、搜尋優化」延後）— 沒說明「快取」是否禁止在 v1 引入；若 E4 引入快取快取現況數量、而 E3 未快取，兩者數字將不一致。建議明寫「v1 不得對 `STOCK_LEVEL` 現況做任何快取」。

---

## 5. 建議新增／收緊的 AD 總表

| 編號 | 名稱 | 狀態 | 解決的分歧 |
| --- | --- | --- | --- |
| AD-19 | 跨 app 公開 use case 介面清單 | 新增 | D2, D3, D6, D10, D13 |
| AD-20 | 庫存現況的唯一真相（STOCK_LEVEL） | 新增 | D2 |
| AD-21 | 銷貨扣減契約：位置、批次、交易與列鎖 | 新增 | D3, D14 |
| AD-22 | 批次消耗明細與 FIFO 排序鍵 | 新增 | D4 |
| AD-23 | 庫存異動類型為封閉列舉（沖銷類型存在） | 新增 | D1, D11, 沖銷回加批次 |
| AD-24 | 銷售用途扣減的雙向可驗證（連結表） | 新增 | D5 |
| AD-25 | 調貨單的 home 與同步呼叫 | 新增 | D6 |
| AD-26 | Actor 傳遞契約與 actor 快照 | 新增 | D7 |
| AD-27 | 業務編號完整清單與 counter 表取號 | 新增 | D9 |
| AD-28 | 欄位 home 唯一性表 | 新增 | D10, D1 |
| AD-29 | 事實的唯一 home 與欄位權威（銷貨三表） | 新增 | D1 |
| AD-30 | 封閉列舉與值域的單一事實來源 | 新增 | D11 |
| AD-31 | 跨 app 查詢口徑與「有成本」定義 | 新增 | D13 |
| AD-32 | 共用層不得容納領域資料（core 無 model） | 新增 | 散文規則 1, 2 |
| AD-2 | 補「任何 app 不得寫入其他 app 的 model」＋ accounts/core 讀取白名單 | 收緊 | D5, D7, 散文規則 1 |
| AD-4 | 補「檢查與扣減同交易同鎖」 | 收緊 | D14 |
| AD-5 | 補 codename 命名規則與權限清單維護 | 收緊 | D8 |
| AD-8 | 補編號清單與 counter 實作 | 收緊 | D9 |
| AD-9 | 補捨入順序與型別 | 收緊 | D11 |
| AD-12 | 補封鎖清單、admin 唯讀、軟刪除適用清單 | 收緊 | 散文規則 3 |
| AD-13 | 補 migration 併行規範與 `--check` 關卡 | 收緊 | D12 |
| AD-14 | 修正帳面等式的等號右邊 | 收緊 | D2, D14 |
| AD-16/Deferred | 明寫 v1 不得快取現況 | 收緊 | D2, 散文規則 6 |

---

## 6. 給 spine owner 的建議優先序

1. **先補 AD-19 / AD-20 / AD-21 / AD-22 / AD-29 / AD-24**（S1 的骨架：事實 home、現況真相、扣減契約、批次消耗、銷貨三表、雙向可驗證）。這六條不補，E3 與 E4 平行實作幾乎必然對不上。
2. **再補 AD-25 / AD-26 / AD-30**（actor 契約、調貨單 home、列舉值域）—— 這三條是 E1 與其餘 epic 的介面契約，越晚補，E1 就要改別人已寫好的程式。
3. **最後補 S2/S3 與可強制性修補**（AD-27 / AD-28 / AD-31 / AD-32 及各 AD 的收緊）。
4. **把散文規則提升為 AD**：方向規則、`STOCK_LEVEL` 不得被彙總取代、`core` 不得有 model、v1 不得快取現況。

---

## 7. 本次審查未涵蓋（誠實揭露）

- 未實際建立 Django 專案或執行 migration，AD-13「可從空庫一次跑完」未經實測。
- 未檢視任何 story 層級檔案（本 initiative 尚無 story），因此「兩 agent 平行實作」的具體落點是依 epic 邊界推演；epic ticket 已提供部分答案（如 E4 明寫「調貨單的建立與移出／移入異動由 E3 執行」、「成本彙總與 FIFO 結算由 E4 使用」），但 **spine 本身未把這些歸屬寫成規則**，因此本審查仍以 spine 為準判定分歧成立。
- PRD FR-17 的折扣率表述（「10% 記為 0.1」vs「0～100% 範圍」）本身矛盾，AD-30 採「值域 0～1、顯示為百分比」的解讀，須由 PRD owner 確認。
