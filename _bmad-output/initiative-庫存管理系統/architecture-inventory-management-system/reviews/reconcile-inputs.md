# 輸入對帳：架構 Spine vs  Initiative／PRD／Addendum

- 對象 spine：`_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`
- 對帳輸入：
  1. Initiative：`initiative-庫存管理系統.md`（R1～R20、Constraints 1～9、Done when、Boundaries）
  2. PRD：`prd-inventory-management-system.md`（FR-1～FR-20、UJ-1～UJ-4、§4.6 NFR、§5／§6.2 非目標、§7 SM、§8 開放問題、§9 假設索引）
  3. Addendum：`addendum.md`（§A 架構模式、§B 技術棧、§C 憑證、§D 資料庫邊界、§E 設計流程、§F 擱置決定）
- 方法：逐條比對 spine 的 AD-1～AD-18、Conventions、Stack、Structural Seed、Capability Map、Deferred，判斷每一條輸入需求是否被「AD／Convention／Deferred／Capability Map」任一處承接。
- 判定口徑：
  - **未落地**：輸入中有明確要求，但 spine 全文找不到承接條文。
  - **矛盾**：spine 條文與輸入規則方向相反，或 spine 宣稱的規則在現況下不成立。
  - **降級**：輸入中是硬性約束，spine 把它列進 Deferred。
  - **發明**：spine 主張了規則，但無法回溯到任何輸入（標為「來源合理但無輸入依據」）。

---

## 一、致命缺口（Critical）——硬性需求完全未落地

### G-01｜FR-1／R1 的登入失敗鎖定與統一錯誤訊息，無任何 AD 承接

- **輸入位置**：PRD FR-1（Consequences：「登入失敗一律回應『帳號或密碼錯誤』」，並假設「同一帳號連續登入失敗 5 次暫時鎖定 15 分鐘」）；PRD §9 假設 1；Initiative R1（「密碼錯誤一律回應『帳號或密碼錯誤』，同一帳號連續失敗 5 次暫時鎖定 15 分鐘」）。
- **Spine 現況**：AD-5 只談權限落地，AD-6 只談 session + CSRF + 同源 proxy。**全文沒有任何一條規則描述登入失敗計數、鎖定時長、鎖定期間回應、錯誤訊息字串，或「不得透露帳號是否存在」**。Capability Map 的「R1 登入與錯誤處理 → AD-1, AD-5, AD-6, AD-17」實際上只涵蓋了「錯誤處理」（AD-17 集中式 exception handler），登入的業務規則整條掉出來。
- **缺口性質**：R1 在 spine front matter 標示為 `binds`，但沒有 AD-5/AD-6/AD-17 的規則文字對應到「鎖定」。這條需求會在 E1 實作時被漏掉。
- **具體修法**：新增 **AD-19 — 登入失敗計數與帳號鎖定**，Rule 建議：
  - 登入失敗一律回應固定訊息「帳號或密碼錯誤」，不得區分帳號不存在／密碼錯誤（回應文字與錯誤碼皆不得洩漏帳號存在性）。
  - 以 (帳號, 來源) 為鍵累計連續失敗次數；達 5 次後鎖定 15 分鐘，鎖定期間即使密碼正確亦拒絕登入；鎖定期屆滿或成功登入即歸零計數。
  - 計數與鎖定狀態存於 `accounts`（DB），不得只放 session／記憶體；時間基準依 AD-10 以 UTC 儲存。
  - 將 R1 重新綁定至 AD-6 + AD-19 + AD-17。

### G-02｜效能基準被誤列為 Deferred，硬性 NFR 降級

- **輸入位置**：PRD §4.6 效能：「在 1,000 筆商品、10,000 筆庫存異動的測試資料集下，清單與明細查詢 2 秒內回應（不含報表彙總與匯出）」；PRD §9 假設 20；Initiative **Constraint 5（查詢效能）** 逐字承接。
- **Spine 現況**：Deferred 表第二列「報表、快取、搜尋優化｜v1 以清單與明細呈現；**1,000 商品／10,000 異動的查詢基準靠索引即可達成**｜v2 專案」——把效能基準與「報表／快取／搜尋優化」綁在一起送進 v2，等於宣告 v1 不承擔此基準。AD-14 測試紀律只要求帳面等式測試，**沒有任何效能測試**；Stack／Structural Seed 也沒有索引策略章節（ERD 節提及 STOCK_LEVEL／STOCK_MOVEMENT，但未指定任何 index）。
- **缺口性質**：這是**降級 + 未落地**雙重問題。Constraint 5 是 Initiative 明列的硬約束，spine 卻把它歸入 v2；而 spine 又自己宣稱「靠索引即可達成」——這是一個未經設計、未經驗證的樂觀假設，沒有任何 AD 承擔索引設計責任。
- **具體修法**：
  1. 從 Deferred 移除效能基準，把 Deferred 條目改寫為「報表、快取與進階搜尋最佳化 → v2」，並註明「1,000 商品／10,000 異動、2 秒內回應的基準由 AD-20 承擔」。
  2. 新增 **AD-20 — 查詢效能基準與索引策略**：Rule 建議——`ITEM(name)`、`STOCK_LEVEL(item, location)`、`STOCK_MOVEMENT(item, occurred_at)`、`STOCK_MOVEMENT(batch)`、`SALES_ORDER(created_at)`、`SALES_ORDER_LINE(order)` 必建索引；「清單與明細查詢」定義為商品清單、庫存現況清單、異動明細、銷貨紀錄清單；固定 seed 產出 1,000 商品 + 10,000 異動，於此資料集下上述查詢 P95 < 2 秒；此基準納入 AD-14 的必跑測試（pytest-benchmark 或以查詢計時斷言）。

### G-03｜使用者密碼的「單向雜湊儲存」未被任何 AD 涵蓋

- **輸入位置**：PRD FR-1 Consequence（密碼錯誤不得透露帳號是否存在）+ 假設「密碼以單向雜湊儲存」；PRD §4.6 安全「密碼不可逆雜湊；憑證不得硬編碼於程式碼、文件或版控」；Initiative **Constraint 2**（「密碼以單向雜湊儲存；連線憑證由外部檔案提供」）；Addendum §C。
- **Spine 現況**：AD-15「資料庫與憑證」只規範**連線憑證**（pgpass.conf / `PGPASSFILE`），**全文沒有出現「使用者密碼雜湊」「password hashing」「Django password hashers」任何字樣**；AD-6 認證也只講 session/CSRF。Capability Map R1/R2/R20 皆未綁到任何雜湊相關規則。
- **缺口性質**：兩種密碼（使用者密碼 vs 資料庫連線密碼）在 spine 只處理了後者。若照 spine 實作，最容易出現的後果是「使用者密碼明文存 User 表」——這直接違反 PRD §4.6 與 Constraint 2 的首要安全條款。
- **具體修法**：在 AD-6 補一條 Rule（或另立 AD-19 的子條）：使用者密碼一律以 Django 預設之 `PBKDF2`（或 `Argon2`）hash 儲存，設定 `PASSWORD_HASHERS` 不得降級為 MD5/SHA1；`User.password` 欄位不得為明文；migration 與測試 fixture 中不得出現可登入的明文密碼（測試帳號以 factory 產生並標記）。同時把 Constraint 2 明確拆成兩條規則（使用者密碼雜湊 / 連線憑證外部化），讓 AD-6 與 AD-15 各承載其一。

### G-04｜「批次」未納入 append-only / 不可軟刪除清單

- **輸入位置**：Initiative Boundaries「不可改變：交易類資料（**庫存異動、銷貨紀錄、批次**）不得刪除或軟刪除」；Addendum §D 補充「交易類資料（**庫存異動、銷貨紀錄、批次**）一律不刪除、不軟刪除，僅追加或反向沖銷」；PRD FR-9（批次記錄）、FR-11（入庫引用批次成本）。
- **Spine 現況**：AD-12 的 Rule 寫「**庫存異動與銷貨紀錄**不得 `update()`／`delete()`」——**批次被漏掉**；AD-11 只說「批次原始資料不可被彙總值取代」與 FIFO 成本基準，**沒有任何不可變更／不可刪除的宣告**；AD-8 只說「編號建立後不可修改」，語意限於編號本身，不等於整筆批次不可動。
- **缺口性質**：未落地。批次是成本追溯（FIFO、R18 毛利）的根基，若可被改單價或刪除，AD-11 的成本基準與 SM-2 帳面一致性都會被破壞；且 AD-12 宣稱的「交易類資料僅追加」與 spine 自己的 ERD（`ITEM ||--o{ BATCH`）不一致。
- **具體修法**：修改 AD-12 為「**庫存異動、銷貨紀錄與採購批次**均僅追加，不得 `update()`／`delete()`／`is_active`；經理層（manager）層封鎖 update/delete，僅提供 append 與查詢；銷售營收與庫存的撤銷以反向沖銷紀錄表達」。同時在 AD-11 補一句「批次單價與數量一經寫入即不可修改」以消除與 AD-8 的語意模糊。並在 Capability Map 的 R9（採購批次）補綁 AD-12。

### G-05｜「毛利即時顯示」與「成本未設定」語意，未被架構契約承載

- **輸入位置**：PRD UJ-3（「**即時顯示**折後金額與毛利，小美當場回報客戶」）、PRD FR-18（「毛利 = 銷貨金額（折後）− 成本，並**與建議售價同時顯示**」「商品無任何入庫成本紀錄時顯示『**成本未設定**』**而非 0**，避免誤判毛利」）、PRD FR-16（**可先存草稿**，草稿不扣減庫存）、PRD FR-17（折後金額 = 原價合計 ×（1 − 折扣率））；Initiative R16/R17/R18。
- **Spine 現況**：
  - AD-7（API 契約）只定義路徑前綴、snake_case、錯誤包絡、分頁過濾，**沒有任何「報價試算／quote preview」端點**；AD-11／AD-9 只定義成本與捨入規則。
  - Capability Map R16 → sales，AD-3/AD-4/AD-9/AD-14，未提「草稿」狀態與「草稿不產異動、不佔用庫存」；AD-17 出現「狀態衝突」例外，暗示有狀態機，卻沒有任何 AD 定義銷貨單的狀態（草稿／已送出／已沖銷）與各狀態下的庫存效果。
  - **沒有任何規則定義「成本未設定」的傳輸語意**（回傳 `null` 而非 `0`，或以列舉值／錯誤碼表達）；AD-9 只規定「單價、總價、銷貨金額為 `Decimal(12,2)`」，在成本缺失時會迫使實作者填 0——正是 PRD 明文禁止的行為。
- **缺口性質**：未落地。這是 PRD 三處獨立陳述的行為期待（UJ-3 高潮 + FR-18 兩條後果 + FR-16 草稿），spine 全部沒有承接。
- **具體修法**：新增 **AD-21 — 銷貨試算與缺成本語意**：
  - 提供唯讀的「報價試算」use case／端點（以商品清單 + 數量 + 折扣率 + 選定位置計算可用量、可消耗批次與 FIFO 成本、試算毛利），**不寫入任何 model**；前端據此在送出前顯示折後金額與毛利，滿足 UJ-3 的即時顯示。
  - 成本缺失時，成本欄位回傳 `null` 且附 `cost_status: "unset"`（或等價旗標），API 契約明文禁止以 0 代表缺成本；前端顯示字串「成本未設定」。
  - 銷貨單狀態機由 AD-3 涵蓋：草稿（不產生異動、不佔用庫存、不計毛利）→ 已送出（單一 transaction 內產生銷貨紀錄、用途＝銷貨的庫存異動並扣減庫存）→ 已沖銷（反向沖銷）；同一商品不得於同一單重複列示。

### G-06｜課業評分標準的優先序與驗收門檻，spine 未承接

- **輸入位置**：PRD §4.6 效能條後的 NOTE：「**若課業評分另有效能標準，以評分標準為準**」；Initiative Boundaries 觸碰點：「**課業評分標準** — 外部輸入，**影響驗收門檻**；owner: 無（使用者）」。
- **Spine 現況**：全文搜尋不到「評分」「課程」「課業標準」等字眼；Deferred 第一列只寫「課業 v1 以本機部署驗收，無生產營運需求」，談的是**部署驗收**而非**評分門檻**；Stack／Environment／AD 皆未表達任何「外部文件優先」的優先序規則。
- **缺口性質**：未落地。下游 E1～E4 的 story 拆解會假設 PRD/架構是最高依據，而 PRD 自己在 §4.6 明確讓位於評分標準——這條優先序若不寫進 spine，任何一方都不知道衝突時聽誰的。
- **具體修法**：在 spine 前言或 Consistency Conventions 新增一條「**優先序規則**」：需求優先序為 `課業評分標準 > PRD／addendum > 本 spine > 實作慣例`；當評分標準與本 spine 的效能基準、部署方式或功能範圍衝突時，以評分標準為準並由 `bmad-architecture` 回修 spine。並在 Deferred 的「課業 v1 以本機部署驗收」一列補註「評分標準未載於本 spine，實作前須由使用者提供並比對」。

---

## 二、次要缺口（Medium）

### G-07｜Constraint 1「參數化查詢」無 AD 承接

- **輸入位置**：Initiative **Constraint 1**（prd §4.6）；PRD §4.6 安全第一句：「所有資料存取不得以字串拼接 SQL，必須使用參數化查詢」。
- **Spine 現況**：全文無「參數化」「raw SQL」「SQL 注入」等字眼。Django ORM 隱含安全，但 spine 允許 view 直接讀 model（AD-2），實作者仍可能使用 `raw()` 或 `cursor.execute()` 做報表／匯出查詢。
- **修法**：於 AD-3（service 層）或新增 AD-19 的資料存取子條補：「所有資料存取一律經 Django ORM；如因效能或報表需要使用 `raw()`／`cursor`，必須使用參數化佔位符並經 code review 檢查，禁止 f-string／`%`／`+` 拼接 SQL 字串」。並在 AD-14 加入靜態檢查（例：`django-guard` 或 grep 規則）作為可執行證據。

### G-08｜權限矩陣的非對稱細節與「前端畫面可見性」未落地

- **輸入位置**：PRD FR-2 權限矩陣（7 列 × 4 角色，含非對稱項：「商品與庫存查詢」四角色全可（會計唯讀）、「水位與待補貨清單」採購可寫、**銷售唯讀**、會計唯讀、「銷貨單與調貨單」僅銷售可、「毛利與成本檢視」銷售與會計可、「帳號與角色指派」僅倉管）；PRD FR-2 Consequence「以未授權角色呼叫該操作時系統拒絕並回應明確的權限錯誤」；PRD FR-14「**銷售與倉管人員**……可建立調貨單」；Initiative R2、Constraint 8（角色固定四種不可自訂、會計唯讀）；PRD §9 假設 2。
- **Spine 現況**：AD-5 說「PRD FR-2 的權限矩陣展開為 permission codename，由 `core/permissions.py` 集中宣告；每個 view 宣告所需權限，越權請求在 view 層被拒絕（403）；會計角色的 view 一律唯讀」。**矩陣本身沒有被展開寫進 spine**（讀者必須回到 PRD 才能知道哪些讀寫組合成立），且：
  - 「每個 view 宣告所需權限」是**單一權限**模型，但矩陣需要**讀／寫分離**（如水位清單：採購可寫、銷售與會計唯讀）。AD-5 未定義唯讀變體的表達方式（例如同一 view 的 GET 與 POST 分別要求 `stock.reorder_level.view` / `stock.reorder_level.change`）。
  - AD-5 的 Prevents 寫「避免只靠前端隱藏按鈕」，但矩陣第一列要求**角色只能存取允許的畫面**（R2 原文：「各自只能存取權限表允許的**畫面**與操作」）。Spine 沒有任何規則說明前端如何得知登入者角色與可見功能集（登入回應是否帶回 roles/permissions 清單、`features/` 目錄如何依權限過濾）。
  - 「一張調貨單只對應一個目標倉庫」「調貨單建立後即生效、不需審批」（PRD FR-14 假設 14、§6.2 v2 排除審批流）在 spine 沒有落地條文，Capability Map R14 亦未綁。
- **修法**：
  1. 於 AD-5 補入完整矩陣展開表（模組 × 角色 × 讀/寫），並定義唯讀以 `view` / 變更以 `change` 兩組 codename 表達，會計角色不指派任何 `change` 權限。
  2. 補：「登入成功回應包含使用者的角色代號與權限 codename 集合；前端據此過濾選單與路由，後端仍以 view 層權限檢查為最終裁決（前端隱藏不等於授權）」。
  3. 補：「角色固定四種（倉管／採購／銷售／會計），不可新增或自訂，權限自訂與審批流排除在 v1 之外（PRD §6.2）」。
  4. 補：「調貨單一單一目標倉庫、建立後即時生效、無審批流程」。

### G-09｜商品主檔的「建議售價／預計毛利」欄位，與 AD-11 的禁令語意重疊且無處安放

- **輸入位置**：PRD FR-4（商品主檔含「建議售價與預計毛利」，必填為商品編號／名稱／供應商）；PRD FR-18（建議售價與預計毛利為**商品層級設定**）；PRD §9 假設 4（庫存數量、批次與採購單價**不由建檔填寫**）。
- **Spine 現況**：AD-11 Rule 末句「**不得在批次或商品表保存彙總成本欄位**」；AD-9 只說單價／總價／銷貨金額為 `Decimal(12,2)`；Capability Map R4 → catalog，governed by AD-1/AD-2/AD-8（**沒有任何 AD 指定 Item 上的建議售價／預計毛利欄位**）；R18 → sales（計算）+ catalog（批次成本），把「建議售價」歸給了 sales。
- **缺口性質**：架構歧義 + 未落地。實作者依 AD-11 的字面禁令，可能把「預計毛利」視為彙總成本欄位而不敢放，或反過來把即時計算的成本寫進 Item 表而違反 AD-11；同時 PRD FR-18 要求毛利「與建議售價同時顯示」，這需要商品層級的建議售價存在。
- **修法**：於 AD-11 補一句排除：「本禁令僅針對**由異動累計而得的彙總成本欄位**；商品層級的**建議售價**與**預計毛利（設計值，非實際結算成本）**屬設定類欄位，允許存於 `Item`（或 `catalog` 專表），與 FIFO 結算成本分離命名（例如 `suggested_price` / `planned_margin`），並於 AD-9 宣告其型別為 `Decimal(12,2)`」。在 Capability Map R4 補綁 AD-9 與 AD-11。

### G-10｜三個仍開放的 PRD 問題與兩個未定義的行為規則，spine 未記錄

- **輸入位置**：PRD §8.1 第 1、2 項（「客戶寄貨」是否視為已銷貨並計毛利；折扣是否可疊加）；PRD §8.2 第 6 項（倉庫／位置編碼格式須與公司既有規則對齊，現為暫定值 `A1`、`A-03`）；PRD §8.3 第 7 項（退貨流程是否納入 v1）；Initiative Notes 三則 Open question 仍掛在 `epic-sales-and-margin` 名下。
- **Spine 現況**：Deferred 表**沒有任何一列對應這三項未定案**，等同對下游宣告「已無待決事項」；AD-12 只寫「取消銷貨以反向沖銷紀錄表達」，未標註「退貨流程未定案」。
- **修法**：Deferred 表新增三列：「客戶寄貨是否計毛利 → 影響領用／銷貨的毛利歸屬，PRD §8.1 待決，v1 沿用『不計毛利』預設」、「折扣是否可疊加 → v1 沿用一階百分比不疊加，PRD §8.1 待決」、「退貨流程 → v1 僅支援取消銷貨反向沖銷，退貨不納入，PRD §8.3 待決」；並在 AD-4 或 AD-12 內註「倉庫／位置編碼格式暫定值 A1／A-03，與公司既有規則對齊後可能變更（PRD §8.2 第 6 項）」。

### G-11｜搜尋排序規則（精確名稱優先）與「可用量」的定義未落地

- **輸入位置**：PRD FR-5 假設（「精確相同名稱優先於部分符合」）、PRD §9 假設 5；PRD FR-15（「各倉可用量加總**不得大於總庫存**」）、PRD FR-16（草稿銷貨單）。
- **Spine 現況**：AD-7 只說「分頁與過濾沿用 DRF 慣例」；Capability Map R5 → stock + catalog，AD-2/AD-3/AD-14，**沒有任何排序規則**；R15 → sales + stock，AD-2/AD-4，**沒有定義「可用量」到底是現況量、扣掉草稿佔用後的量，或扣掉安全存量後的量**——這直接影響 UJ-3「面紙只剩 C 倉有貨」的判斷與 FR-15 的「各倉可用量加總不得大於總庫存」是否成立。
- **修法**：AD-7 補：「商品搜尋預設排序＝名稱完全相符優先，其後為部分相符，再依商品編號穩定排序；分頁預設 20、上限 100」。新增可用量定義（「可用量 = 該位置現況量 − 已被已送出銷貨單／草稿鎖定的數量 − 該倉安全存量設定（如有）；顯示時必須同時回傳現況量與可用量，且各倉可用量加總 ≤ 總現況量」）。

### G-12｜「不可追溯來源」的 spine 規則（發明）

以下 spine 規則在 Initiative／PRD／Addendum 中找不到直接依據。多數屬合理的架構判斷，但未標示來源，會讓後續 story 誤以為是需求或可能與需求衝突，建議在 spine 中標註「架構決策，來源：spine」：

| Spine 條文 | 內容 | 輸入對應 | 建議 |
| --- | --- | --- | --- |
| AD-10 | 資料庫與 API 一律 UTC，顯示層轉 `Asia/Taipei`，業務日期另存 date | 無（PRD 僅有「日期」欄位） | 合理；標註為 spine 決策，並說明不影響 PRD 驗收語意 |
| AD-9 | 捨入一律 `ROUND_HALF_UP`、型別 `Decimal(12,2)` | PRD 只說「小數點後兩位」，未指定捨入模式與精度 | 合理；應確認 `Decimal(12,2)` 足夠（金額上限 10^10） |
| AD-7 | 路徑前綴 `/api/v1/`、snake_case、錯誤包絡 `{code, detail, field_errors}` | 無具體契約格式要求 | 合理；但應與 PRD FR-4「缺項時指出缺哪一欄」與 FR-17「折扣率超出範圍拒絕」對接，明示 `field_errors` 對應的欄位鍵 |
| AD-8 | 採購批次流水號「序號在同一日內**全域**遞增」 | PRD FR-9：「同一天內全域遞增、不重複（**跨供應商共用同一序號流水**）」 | ✅ 一致，非發明；但 AD-8 未寫出「跨供應商共用」這個關鍵限定，易被實作誤解為「每供應商各自計號」→ 建議補明 |
| AD-16 / Deferred | WhiteNoise + gunicorn 同源供應；容器化列入 v2 | Addendum 未提 Docker；Initiative 未提部署方式 | Deferred「容器化」即等同「不使用 Docker」，但應在 Environment 或 AD-16 明寫「v1 不使用 Docker／容器化，本機部署」以避免下游自行引入 |
| Stack 表 | Django 6.1、DRF 3.17.1、psycopg 3.3.7、Vite 8.0、React 19.2.7、pytest 8.4.2、pytest-django 4.11.1、factory_boy 3.3.3、WhiteNoise 6.12.0、gunicorn 25.3.0 | 輸入只說「候選，未定案」；AGENTS.md 僅確認 Node 22.18.0 / npm 10.9.3 / Python 3.14.7 / PostgreSQL 18.6 | **版本清單無輸入依據且未標示來源與驗證方式**；至少 Django 6.1、Vite 8.0 等版本需在安裝前實際確認存在且互相相容，否則會在 E1 第一個 story 就卡住。建議加一欄「來源／驗證日期」 |
| Deferred | 「前端狀態管理與資料快取方案 → 由 E1 選定」 | 無 | 合理，但與 AD-16「前端功能目錄 `features/` 對應四個 app」並存時需說明 `features/` 不得自行引入跨 app 狀態共享，避免 E2～E4 各自選一套 |

---

## 三、矛盾清單（Spine 與輸入／現況直接衝突）

### M-01｜AD-15 宣稱「密碼不得出現在文件」，但專案既有文件 `AGENTS.md` 已含明文密碼

- **Spine 現況**：AD-15 Rule：「密碼不得出現在程式碼、**文件**、migration 與版控中。」
- **現況**：專案根目錄 `AGENTS.md` 第 47 行直接寫著 `內容格式：localhost:5432:*:postgres:12345678`——即明文密碼已存在於專案文件中（而 `AGENTS.md` 會被每次開啟專案自動載入進 AI 上下文）。這同時違反 PRD §4.6、Initiative Constraint 2 與 Addendum §C。
- **修法**：spine 除宣告規則外，應在「觸碰點／環境」段落加一條既況修正行動：`AGENTS.md` 中的 `pgpass.conf` 內容格式行必須改為不含明文密碼（例如寫成 `localhost:5432:*:postgres:<密碼>`，密碼由 `pgpass.conf` 自行提供）；並把 `AGENTS.md` 的清理列為 E1 第一個 story 的前置任務（與 AD-15 同一個 story 落地）。**注意：本次對帳僅記錄，不代為修改 `AGENTS.md`。**

### M-02｜Deferred 表把 Constraint 5（效能）與 v2 綁定，與 Initiative 硬約束直接衝突

- Initiative 把「查詢效能」列為 **Constraint 5**（編號為 1～9 的硬約束段），spine 卻把同一條寫進 Deferred 並標註「v2 專案」。詳見 G-02。
- **修法**：如 G-02 第 1 點。

### M-03｜AD-12 的交易類資料清單少一項，與 Initiative／Addendum 的「不可改變」清單不一致

- Initiative Boundaries 與 Addendum §D 皆列三項（庫存異動、銷貨紀錄、**批次**），AD-12 只列兩項。详见 G-04。

---

## 四、已妥善落地（無需再動，供對帳完整性）

| 輸入要求 | 承接處 | 判定 |
| --- | --- | --- |
| 銷售扣減唯一入口（Constraint 6、FR-12／FR-16） | AD-4「銷售用途的庫存扣減只能經銷貨 use case（領用用途不得為『銷貨』）」 | ✅ 一致 |
| 跨倉只走調貨單（Constraint 7、FR-13／FR-14） | AD-4「任何跨倉庫存變動必須帶有調貨單」+ AD-14 帳面等式測試 | ✅ 一致 |
| 一專案一資料庫（Constraint 9、Addendum §D） | AD-15「單一 PostgreSQL 實例上的單一 schema（本專案專用 `AILearn`）」 | ✅ 一致（注意 D 段「權限隔離亦落在同一 DB，由應用層控管」與 AD-5 一致） |
| FIFO 成本基準（Addendum §F、FR-18、§8.1） | AD-11 完整承接，且明列「不得在批次或商品表保存彙總成本欄位」 | ✅ 一致（僅有 G-09 的語意澄清需求） |
| 交易完整性（Constraint 3） | AD-3 `transaction.atomic()` + AD-4「超領時整筆回滾」 | ✅ 一致 |
| 僅追加稽核（Constraint 4，庫存異動／銷貨紀錄部分） | AD-12 | ✅ 一致（僅缺批次，見 G-04） |
| 連線憑證外部化（Constraint 2 後半、Addendum §C） | AD-15 + Conventions「設定以環境變數注入（`PGPASSFILE`）」 | ✅ 一致（但見 M-01） |
| 帳面等式驗收（Done when 2、SM-2） | AD-14 測試組 `入庫 − 領用 − 調出 + 調入 − 銷貨 = 0` | ✅ 一致 |
| 可追溯性（Done when 3、SM-3） | AD-18（操作人員、時間、數量、用途、批次永久保存） | ✅ 一致 |
| 四個 app 對應四個 epic | AD-1 + Structural Seed | ✅ 一致 |
| 依賴方向單向、跨 app 寫入走 service | AD-2 | ✅ 一致 |
| 架構模式定案（Addendum §A／§F：MVVM vs MVC 待定） | Spine 採 Django MVT + service 層（對應「UI 與業務邏輯分離」的 MVVM 傾向） | ⚠️ **未被明確裁決**（見下） |
| ER 設計工具（Addendum §E／§F：dbdiagram.io） | Spine 用 mermaid `erDiagram` | ⚠️ **未被明確裁決**（見下） |
| 建庫流程（Addendum §E） | AD-13 migrations + AD-15 既有 `AILearn` | ⚠️ 部分 |

### 兩項未明確裁決的技術輸入

- **MVVM vs MVC（Addendum §A／§F）**：spine 的 paradigm 寫「Django 分層單體（MVT）+ service 層」，實質對應簡報「核心目標是將 UI 與業務邏輯／資料模型徹底分離」的 MVVM 傾向，但 spine **沒有記錄這是對 §F 待決項的裁決**。建議在 spine 前言或 Stack 段補一句：「Addendum §F 的『架構模式』待決項於此定案為 Django MVT + service 層（view/template 與領域邏輯分離，對應簡報 MVVM 傾向）；Django MVT 非 MVC 之原意，UI／業務分離的目標由 service 層達成」。
- **ER 圖工具 dbdiagram.io（Addendum §E 第 3 步、§F）**：spine 直接以 mermaid `erDiagram` 呈現 ERD，**未說明是否取代簡報指定的 dbdiagram.io 流程**。建議補：「本 spine 的 ERD 採 mermaid 描述，取代簡報建議的 dbdiagram.io 流程；DDL 由 Django migrations 產生（AD-13），不另行手寫 DDL 檔」。這同時讓 Addendum §E「以文字檔提供憑證給 AI 開鎖」的步驟有明確替代。

---

## 五、建議修補動作清單（可直接回寫 spine）

| # | 動作 | 對應缺口 |
| --- | --- | --- |
| 1 | 新增 **AD-19 登入失敗計數與帳號鎖定**（5 次／15 分鐘／統一訊息／不洩漏帳號存在性／計數存 DB） | G-01 |
| 2 | 新增 **AD-20 查詢效能基準與索引策略**（1,000 商品／10,000 異動、2 秒、必要索引、納入測試）；自 Deferred 移除效能基準 | G-02 |
| 3 | AD-6 或 AD-19 補「使用者密碼單向雜湊（PBKDF2/Argon2）儲存，不得明文」 | G-03 |
| 4 | AD-12 補入「**批次**」為交易類僅追加資料；AD-11 補「批次內容寫入後不可修改」；Capability Map R9 綁 AD-12 | G-04 |
| 5 | 新增 **AD-21 銷貨試算與缺成本語意**（quote preview 端點、成本缺 null 不為 0、銷貨單狀態機與草稿） | G-05 |
| 6 | 新增「需求優先序規則：課業評分標準 > PRD/addendum > spine > 實作慣例」並於 Deferred 註明評分標準尚未載入 | G-06 |
| 7 | AD-3 補「一律 ORM／參數化查詢，禁止字串拼接 SQL」；AD-14 補靜態檢查證據 | G-07 |
| 8 | AD-5 補入完整權限矩陣展開（讀/寫分離 codename）、登入回應含角色與權限、角色固定四種；補調貨單一單一目標倉且即時生效 | G-08 |
| 9 | AD-11 補排除條款（建議售價／預計毛利為設定類欄位，允許存於商品主檔）並與 AD-9 綁定 | G-09 |
| 10 | Deferred 新增三列（三個未決問題）並於 AD-4／AD-12 標註編碼格式為暫定值 | G-10 |
| 11 | AD-7 補搜尋排序規則（精確優先）與分頁預設；新增「可用量」定義與加總不變式 | G-11 |
| 12 | 為 AD-7／AD-9／AD-10／Stack 標註來源為「spine 決策」，Stack 加「來源／驗證日期」欄並實際驗證版本存在性 | G-12 |
| 13 | AD-15 增列既況修正行動：`AGENTS.md` 移除明文密碼，列為 E1 第一個 story 前置任務 | M-01 |
| 14 | 前言／Stack 補「MVVM vs MVC 定案說明」與「ER 工具／DDL 流程取代 dbdiagram.io」 | 第四節 |

---

*本文件為對帳分析，未修改任何 artifact。*
