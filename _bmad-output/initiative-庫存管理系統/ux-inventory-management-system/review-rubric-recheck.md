# Spine Pair Re-check — 庫存管理系統（DESIGN.md + EXPERIENCE.md）

受審標的（複審，未修改）：
- `DESIGN.md`（design-spine，271 行）
- `EXPERIENCE.md`（experience-spine，290 行）
- 對照前次審查：`review-rubric.md`（48 筆 findings：2 critical / 13 high / 21 medium / 12 low；本次複審依 rubric 逐節逐條編號 F1.1～F8.4）
- 來源：`../../initiative-庫存管理系統.md`、`../../prd-inventory-management-system/prd-inventory-management-system.md`、`../../architecture-inventory-management-system/architecture-inventory-management-system.md`
- Mockups：`mockups/key-login.html`、`key-stock-search.html`、`key-replenishment.html`、`key-sales-order.html`

驗證方法（皆為實測，非信任修訂說明）：
1. 以腳本解析 DESIGN.md frontmatter 建立 126 條完整路徑集合，掃描兩份 spine 內所有 `{...}` 引用（68 種相異樣式）逐一比對。
2. 以 WCAG 2.x 相對亮度公式獨立計算所有文字色／底色對比比值（淺色 `#FFFDF8`／`#F6F1E7`，深色 `#1D1812`／`#14100B`）。
3. 逐筆比對 Colors 散文表 17 列 hex 與 frontmatter 值。
4. 以程式比對兩份 spine 元件表的名稱集合（27 vs 27）。
5. 逐一比對 IA 15 個模組畫面與 State Patterns 矩陣、UJ-1～UJ-6 結構、PRD §2.3／§3／FR-2。
6. 擷取 4 個 mockup 全部 hex／rgba 字面值（含 CSS 變數）比對 frontmatter token。

---

## 一、前次 findings 逐條複查

| id | 前次嚴重度 | 狀態 | 證據（檔案＋行號） |
| --- | --- | --- | --- |
| F1.1 | critical | **fixed** | UJ-5（EXPERIENCE.md:262-268）、UJ-6（:270-276）已補；Component Patterns 新增「領用作業」(:129)、「同倉移轉」(:130)、「調貨單」(:131)；State Patterns 新增領用/移轉/調貨單三組狀態(:163-168) |
| F1.2 | high | **fixed** | UJ-2 邊界（:238 缺單價/數量、已有未到貨批次）、UJ-4 邊界（:260 查無單號→清除條件）皆已補 |
| F1.3 | high | **fixed** | UJ-3 步驟 1 已統一為 `INV-000207 面紙 L 抽取式`／`INV-000208 面紙 擦手紙`（EXPERIENCE.md:244） |
| F1.4 | medium | **partially fixed** | 商品主檔必填(:179)、供應商統編重複(:180)、位置代碼重複(:181)、重複商品(:173)、停用登入/重設密碼(:183-184) 已補；**缺「倉庫編碼唯一」(FR-10)** 與 **「批次流水號 `PO-YYYYMMDD-序號` 同日唯一」(FR-9)** |
| F1.5 | medium | **fixed** | State Patterns 新增「未認證（session 過期，401）→ 導向 `/login` 並記錄 `return_to`」（EXPERIENCE.md:156） |
| F1.6 | low | **partially fixed** | UJ-1 步驟 2 與高潮（:222,:226）實際承載 R5/R3，但 Key Flows 開頭（:217）只說明 UJ-1～UJ-4 對應 PRD，未加 R3/R5 追溯句 |
| F2.1 | critical | **fixed** | colors 改為 flat + `-dark` 平行鍵（DESIGN.md:9-55）；全篇 `{colors.primary}` 等引用現已可解析（腳本驗證：除 5 處 glob 外全部命中） |
| F2.2 | critical | **fixed** | 新增 `accent-text #9E5708`（:52）與 `accent-text-dark #F0B75E`（:53）；實算 light 5.41:1 / dark 9.77:1 通過；`{colors.accent}` 明令僅非文字並揭露「淺色下僅 2.86:1」（:166,:172,:267） |
| F2.3 | high | **fixed** | warning `#8A6200` light 5.40:1 / dark 8.97:1；text-muted `#6E6553` light 5.66:1 / dark 6.06:1，皆 ≥4.5（實測） |
| F2.4 | high | **fixed** | 新增 `border-strong #94856A` / `#857459`（:18-19），實算 3.55:1 / 3.89:1 ≥3；`border` 已降為純分隔線（:155）；mockup 輸入框/按鈕改用 `--border-strong`（mockups/key-stock-search.html:154 等） |
| F2.5 | high | **fixed** | Colors 表 17 列無重複，`warning` 僅一列（:163） |
| F2.6 | medium | **fixed** | `text-muted` + 新增 `muted-tint`/`muted-tint-dark`（:24-25,:48-49）；EXPERIENCE.md:135 已統一為 `{colors.text-muted}` on `{colors.muted-tint}`（實測 4.93:1 / 5.24:1） |
| F2.7 | medium | **fixed** | 新增 `primary/success/warning/danger/info/muted/accent` 七組 tint 與深色對應（:30-31,34-35,38-39,42-43,46-47,48-49,54-55）；mockup `--tint-*` 數值與 frontmatter 完全一致 |
| F2.8 | medium | **not fixed** | glob 引用仍在：`{colors.*}`（EXPERIENCE.md:200）、`{colors.*-tint}`（DESIGN.md:242）、`{components.表格.*}`（:230）、`{components.表單.*}`（:236,237,240）、`{components.圖示.*}`（:252） |
| F2.9 | low | **partially fixed** | `rounded.xs`、`spacing.row-default`、`spacing.row-relaxed`、`spacing.scale-2/5`、`colors.accent-tint/success-tint/danger-tint/info-tint`、`components.版面.sidebar-width/grid-columns/grid-gutter`（與 `spacing.*` 重複）、`components.表單.button-radius/input-border`、`components.焦點.offset` 皆定義但未被任何 `{...}` 引用 |
| F3.1 | high | **fixed** | 庫存查詢列(:231)、銷貨單編輯(:232)、位置選擇器(:234)、批次選擇器(:235)、水位設定(:239)、帳號與角色(:240) 六列已補 |
| F3.2 | high | **fixed** | 應用外框(:119)、頂列(:120)、數值摘要條(:126)、表單(:134)、空狀態(:136) 五列已補 |
| F3.3 | high | **fixed** | 抽屜/分頁器/草稿提示條/骨架載入/通知計數徽章/工具列與圖示/登入表單 皆在兩表同名出現（DESIGN.md:245-252 / EXPERIENCE.md:137-145） |
| F3.4 | medium | **partially fixed** | 兩表 27 個元件名稱已逐字相同（腳本比對集合完全一致）；但散文仍混用「摘要區」(EXPERIENCE.md:175)、「摘要條」(:126,:192) 與元件名「數值摘要條」 |
| F3.5 | medium | **fixed** | 導覽規則明定「語系與色彩模式只在頂列（唯一權威位置）」(EXPERIENCE.md:80) |
| F4.1 | high | **partially fixed** | 領用(:163-164)、移轉(:165-166)、調貨單(:167-168) 三畫面已有狀態列；**但三者皆缺「提交成功」狀態列** |
| F4.2 | high | **partially fixed** | `catalog.duplicate_tax_id`(:180)、`sales.duplicate_item`(:173)、停用登入/重設密碼(:183-184) 已補且沿用 AD-17 機器碼；**缺 FR-10 倉庫編碼唯一、FR-9 批次流水號唯一** |
| F4.3 | medium | **fixed** | 與 F1.5 同（EXPERIENCE.md:156） |
| F4.4 | medium | **fixed** | IA 明示「通知僅為計數指標…v1 不設獨立通知中心頁」(:39)；通知計數徽章行為「點擊導向該模組的待辦清單」(:140) |
| F4.5 | medium | **fixed** | 403 列已區分「導覽層隱藏 vs 直接輸入越權網址/403 畫面」(EXPERIENCE.md:157) |
| F4.6 | low | **partially fixed** | 空狀態規範仍分散三處：Voice and Tone 表(:94)、State Patterns「空資料」(:154)、元件「空狀態」(:136) |
| F5.1 | medium | **partially fixed** | EXPERIENCE.md 已 inline 引用 4 個 mockup（:41,:82,:229,:240,:252），原「視覺參考」表已刪；**但 DESIGN.md 全篇 0 筆 mockup 引用**（腳本掃描確認） |
| F5.2 | medium | **fixed** | 4 個 mockup 全部 hex（42 個淺/深色值）皆命中 frontmatter token；rgba 僅 `rgba(140,74,15,.035)`（= `components.表格.stripe`）與卡片陰影 rgba（= `components.卡片.shadow`） |
| F5.3 | medium | **not fixed** | 仍無「其餘 13 個畫面尚無 1:1 mockup，視覺基準由 DESIGN.md 承載」之說明 |
| F5.4 | low | **fixed** | DESIGN.md:138 已載明方向與配色出自 `.working/direction-bright-workbench.html`、`.working/color-themes-5.html` |
| F6.1 | medium | **fixed** | 新增 `spacing.row-tight: '28px'`(DESIGN.md:89)，敘述改引用 token(:140,:193) |
| F6.2 | medium | **fixed** | 新增 `components.圖示.size-sm/size-md/stroke`(:119-122)，敘述改引用(:218) |
| F6.3 | medium | **fixed** | 新增 `spacing.grid-columns: '12'`、`grid-gutter: '16px'`(:95-96)；「1 位元組」誤植句已改寫為「字元寬度一致因而能垂直對齊」(:195) |
| F6.4 | low | **fixed** | Do's 已改用 `{spacing.row-compact}`、`{spacing.scale-3}`、`{spacing.scale-6}`(:260) |
| F6.5 | low | **not fixed** | 仍逐條重述 PRD §5／§6.2 清單，且同一句宣稱「本文件不重述」(EXPERIENCE.md:290) —— 自相矛盾 |
| F6.6 | low | **fixed** | 「緊湊（桌機優先）」贅詞已收斂(DESIGN.md:140) |
| F7.1 | high | **fixed** | 兩份 spine 皆有 `sources`(DESIGN.md:8 / EXPERIENCE.md:7)，三條相對路徑逐一解析成功（prd / initiative / architecture 皆存在） |
| F7.2 | high | **fixed** | shadcn/ui + Tailwind 已改標為「本 spine 的 UI 層決策（架構 spine 未涵蓋，待 E1 建置時確認）」(EXPERIENCE.md:20)；AD-16 只承載前端建置(:17)、AD-6 承載認證(:18) |
| F7.3 | high | **partially fixed** | 調貨單矛盾已標註為待裁決並列入 Open Questions(EXPERIENCE.md:75,:282) ✅；**但供應商／採購批次對倉管與會計的讀取授權未標註（見 R1）** |
| F7.4 | medium | **fixed** | 68 種 token 引用中 63 種可解析；剩 5 種為 glob（見 F2.8） |
| F7.5 | medium | **partially fixed** | 新增「術語對照」段(:28) 引用 PRD §3（庫存位置/庫存異動/調貨單/領用用途/水位/批次/毛利）；**未涵蓋 PRD §3 的 商品/倉庫/供應商/銷貨單/角色；「異動」(:226) 與「庫存異動」(:64) 仍混用** |
| F7.6 | medium | **partially fixed** | `muted` → `text-muted` 已統一 ✅；「數值摘要條／摘要條／摘要區」仍混用（見 F3.4） |
| F7.7 | medium | **fixed** | 已明文「accent 與 warning 不得同屏近鄰使用，摘要列毛利強調與低於水位警示至少隔一個區塊」(DESIGN.md:174) |
| F7.8 | low | **fixed** | 已補 `description`(DESIGN.md:3) |
| F8.1 | low | **fixed** | DESIGN.md 章節順序仍為 Brand & Style→Colors→Typography→Layout & Spacing→Elevation & Depth→Shapes→Components→Do's and Don'ts；EXPERIENCE.md 必要章節齊備 |
| F8.2 | medium | **fixed** | 新增「斷點行為」四列表(DESIGN.md:200-205)，含 1440/1280/1024/<1024 各區間側欄、表格、摘要列行為 |
| F8.3 | low | **not fixed** | 仍無 IA 示意圖（可選） |
| F8.4 | low | **not fixed** | 仍無「Inspiration & Anti-patterns」節（可選） |

**統計：fixed 33、partially fixed 10、not fixed 5（前次 48 筆中無任何一筆倒退）**

---

## 二、Remaining findings

### R1 [high] IA 權限矩陣仍有未標註的 FR-2 偏差（供應商／採購批次／倉庫位置）
- **位置**：EXPERIENCE.md:66-68（IA 模組與畫面表）、:75（僅標註調貨單一項偏差）
- **問題**：PRD FR-2（prd:83）「供應商與採購批次」欄為 倉管 `—`、採購 `✔`、銷售 `—`、會計 `—`；EXPERIENCE.md:66 給 會計「唯讀可見」、:67 給 倉管「唯讀可見」且讓其看見批次單價（成本）。PRD FR-2 的驗收條件是「以未授權角色呼叫該操作時系統拒絕」，下游若照 spine 實作角色閘門，倉管／會計會看到 PRD 未授權的供應商與成本資料。另 :58 將「庫存現況工作台」標為倉管「可操作」，但 spine 與 PRD 都未定義該頁有任何寫入動作，屬自創權限。
- **修法**：把 :66-67 的倉管／會計欄位改為 `—`（或如調貨單般在 :75 加註說明「與 FR-2 矩陣不一致，建議裁決」並列入 Open Questions）；:58 的「可操作」改為「唯讀可見 + 倉管可執行入庫/領用/移轉入口（跳轉至對應作業畫面）」。供應商與採購批次的唯讀若要保留，須在 Open Questions 增列一列說明理由與裁決人。

### R2 [medium] 可寫入畫面普遍缺少「提交成功」狀態列
- **位置**：EXPERIENCE.md:151-186（State Patterns 矩陣）
- **問題**：矩陣只有「銷貨單｜提交後」(:177) 一列成功狀態；入庫(:160-162)、領用(:163-164)、移轉(:165-166)、調貨單(:167-168)、商品主檔(:179)、供應商(:180)、倉庫與位置(:181)、採購批次(:182)、帳號(:183-184)、待補貨清單／庫存現況工作台 均只有錯誤或空狀態。UJ-1 步驟 5 有成功摘要描述，但狀態矩陣缺位，下游 story-dev 無法直接引用「成功」的統一呈現規格（單號／影響數量／下一步動作）。
- **修法**：為每個可寫入畫面補一行「畫面｜提交成功｜呈現」，內容至少包含：結果摘要（單號或影響筆數）、實際變更（數量、位置、批次）、下一步動作按鈕、以及「成功不帶驚嘆號、說明下一步」的 Voice 規則引用。

### R3 [medium] 兩項唯一性規則仍無可引用的狀態列
- **位置**：EXPERIENCE.md:180-182（相鄰列）、PRD FR-9（prd:156-159）、FR-10（prd:169-172）
- **問題**：PRD 要求「同一天的批次流水號不重複」「倉庫編碼在公司內唯一」「同倉位置代碼唯一」。State Patterns 只覆蓋位置代碼重複(:181)，缺批次流水號重複與倉庫編碼重複；亦無「位置代碼格式『區碼-格位』」的驗證規則，而 Open Questions(:285) 說格式待裁決。
- **修法**：在 State Patterns 補兩列（沿用 AD-17 機器碼命名，例如 `catalog.duplicate_po_number`、`catalog.duplicate_warehouse_code`），並在「倉建與位置」列補格式不符的就地提示；格式未定案的則標為「暫依 Open Questions 暫定值驗證」。

### R4 [medium] EXPERIENCE.md:121 含一個 U+FFFD 替換字元（mojibake）
- **位置**：EXPERIENCE.md:121（側邊導覽列）
- **問題**：原文為「依角色顯示／隱<U+FFFD>項目」，`隱` 後的字元已被寫成 U+FFFD（非法字元），渲染與下游 diff 都會顯示亂碼。全專案掃描確認僅此 1 處（mockup 與其他 md 無）。
- **修法**：改回「依角色顯示／隱藏項目」。

### R5 [low] 5 處 glob token 引用仍非合法路徑
- **位置**：DESIGN.md:230 `{components.表格.*}`、:236/:237/:240 `{components.表單.*}`、:242 `{colors.*-tint}`、:252 `{components.圖示.*}`、EXPERIENCE.md:200 `{colors.*}`
- **問題**：嚴格 resolver 無法解析；且 `components` 的 frontmatter 鍵為「表格／卡片／表單／焦點／圖示／版面」，而 Components 表格的元件名是「資料表格」「銷貨單編輯」等，兩層命名不一致，使 glob 更難對應。
- **修法**：改為具名 token（例：`{components.表格.row-height}`、`{components.表單.input-height}`、`{colors.warning-tint}`），或直接寫成純文字「語意色 token」「表單元件 token」。

### R6 [low] 定義但未引用／重複命名的 token 仍在
- **位置**：DESIGN.md:75 (`rounded.xs`)、:84-85 (`spacing.scale-2/scale-5`)、:91-92 (`spacing.row-default/row-relaxed`)、:34,42,46,54 (`success-tint`/`danger-tint`/`info-tint`/`accent-tint`)、:123-127 (`components.版面.*` 與 `spacing.sidebar-width/topbar-height/grid-columns/grid-gutter` 重複)、:112-115 (`表單.button-radius/input-border/label-gap`)、:118 (`焦點.offset`)
- **問題**：`components.版面` 整組與 `spacing.*` 同值同義，是兩份真相；`success-tint`/`danger-tint`/`info-tint`/`accent-tint` 只存在於 frontmatter，Colors 散文表的 tint 列寫「`{colors.primary-tint}` … `{colors.muted-tint}`」，此範圍記法不含 `accent-tint`；`accent` 若被當作狀態色文字配 `accent-tint`，實測僅 2.54:1（不合格）。
- **修法**：刪除 `components.版面`（版面尺寸一律取 `spacing.*`）或反過來刪 `spacing.*` 只留一份；於 Colors 表補 `accent-tint` 一列並註明「僅用於非文字強調底，不得以 `accent` 為其文字色」；`success-tint`/`danger-tint`/`info-tint` 在「狀態徽章」列明確指定來源；未用到的間距／圓角鍵刪除或在 frontmatter 註明為預留刻度。

### R7 [low] 元件名「數值摘要條」與散文「摘要條／摘要區」不一致
- **位置**：EXPERIENCE.md:126（元件名「數值摘要條」）vs :175（「摘要區毛利」）、:192（「回應更新摘要條」）；DESIGN.md:233
- **修法**：統一為「數值摘要條」，或元件名改為「摘要條」並在兩表同步。

### R8 [low] DESIGN.md 未引用任何 mockup
- **位置**：DESIGN.md 全篇
- **問題**：EXPERIENCE.md 已有 4 個 inline mockup 連結，但視覺契約本身不指向視覺基準，mockup 的「Governed by DESIGN.md § Colors」註解形成單向引用。
- **修法**：於 DESIGN.md「Brand & Style」或「Components」段末加一行「視覺基準見 `mockups/key-stock-search.html`（表格密度）與 `mockups/key-sales-order.html`（毛利著色）」。

### R9 [low] 未說明其餘畫面無 1:1 mockup
- **位置**：EXPERIENCE.md:41,:82 或 IA 段末
- **修法**：加一句「IA 共 15 個畫面，目前僅登入、庫存查詢清單、待補貨清單、銷貨單四個有 1:1 mockup；其餘畫面之視覺基準由 `DESIGN.md` 承載」。

### R10 [low] 「非目標」段落自相矛盾
- **位置**：EXPERIENCE.md:290
- **問題**：同一句前半列舉電商前台、POS、會計總帳…，後半稱「本文件不重述」。
- **修法**：刪掉列舉，只留「完整清單與理由見 PRD §5、§6.2 與 initiative 的 Boundaries」。

### R11 [low] 空狀態規範仍分散三處
- **位置**：EXPERIENCE.md:94（Voice 表）、:154（State「空資料」）、:136（元件「空狀態」）
- **修法**：State Patterns 改為引用元件規則「見元件『空狀態』」，Voice 表保留語氣例句。

### R12 [low] Mockup 註解與 spine 命名有微差
- **位置**：mockups/key-replenishment.html:16,18（「DESIGN.md § Colors：…muted 用於輔助」應為 `text-muted`；「EXPERIENCE.md § Flow UJ-2 step 2」章節名實為「Key Flows」）、mockups/key-login.html:20（深色模式陰影用 `rgba(0,0,0,.4)/(.45)`，與 DESIGN.md:212「深色模式陰影幾乎不可見」不符）
- **修法**：統一註解用語；深色模式 mockup 改以表面亮度表達層次（陰影 alpha 降至 ≤.15 或移除）。

### R13 [low] 術語對照未涵蓋 PRD §3 全部條目
- **位置**：EXPERIENCE.md:28
- **問題**：只列 7 個詞；PRD §3 另含 商品、庫存數量、倉庫、供應商、銷貨單、角色，且「異動」(:226) 與「庫存異動」(:64) 仍混用。
- **修法**：補列剩餘 6 個詞並指明不可改稱的名稱；全篇統一以「庫存異動」為正式詞，縮寫只在畫面標題使用「異動」。

### R14 [low] 選用項未做（沿用 F8.3 / F8.4）
- **位置**：EXPERIENCE.md IA 段、DESIGN.md 末段
- **修法**：可選加一張 IA 流程圖與一節「Inspiration & Anti-patterns」（整理 `.working/` 中被捨棄的三個方向）。本次不阻擋。

---

## 三、已通過的驗證（不列為 finding）

- 所有 `{path.to.token}` 引用（63 種非 glob）皆命中 DESIGN.md frontmatter 實際路徑，含巢狀路徑 `{components.表格.row-height}`、`{components.表單.input-height}`、`{typography.fontSize.body}`、`{typography.fontWeight.semibold}`、`{typography.lineHeight.tight}`、`{colors.primary-tint}` 等。
- Colors 散文表 17 列 hex 與 frontmatter 逐一相符；每個色 token 皆有 light/dark 兩值。
- 對比實測（淺色 surface `#FFFDF8` / 深色 `#1D1812`）：text-primary 14.70/14.37、text-secondary 8.06/8.94、text-muted 5.66/6.06、primary 6.66/7.46、success 5.80/8.18、warning 5.40/8.97、danger 6.68/6.11、info 5.70/6.60、accent-text 5.41/9.77、primary-foreground on primary 6.32/7.84 — 全部 ≥4.5:1。徽章 text-on-tint：primary 5.73/6.35、success 5.17/6.83、warning 4.83/7.63、danger 5.70/5.52、info 4.93/5.59、muted 4.93/5.24 — 全部 ≥4.5:1，且 warning 4.83 符合 spine 自陳的「≥4.8:1」。非文字邊框：border-strong 3.55/3.89 ≥3:1 ✅。`accent`（2.86:1）已由 spine 明令禁止用於正文，不計缺陷。
- 元件名稱集合：DESIGN.md Components 27 列 與 EXPERIENCE.md Component Patterns 27 列 **完全相同**（逐字比對）。
- IA 15 個畫面 × 角色欄位與 PRD FR-2 對照：入庫/領用/移轉（倉管可操作）✅、供應商與採購批次（採購可操作）✅、待補貨清單（採購可操作 + 銷售/會計唯讀）✅、新增銷貨單（銷售可操作）✅、帳號與角色（倉管可操作）✅、調貨單（僅銷售，已標註待裁決）✅；例外見 R1。
- Key Flows：UJ-1～UJ-6 均有具名主角（小陳／小王／小美／小周／小美／小陳）、編號步驟、「**高潮**」節拍、「**邊界**」失敗路徑 ✅；UJ-1～UJ-4 標題與 PRD §2.3 逐字相符 ✅。
- `sources` 三條相對路徑皆可解析 ✅；mockup 的 `Governed by` 所指章節（Colors / Typography / Layout & Spacing / Shapes / Elevation & Depth / Components / Do's and Don'ts / Information Architecture / Component Patterns / State Patterns / Voice and Tone / Accessibility Floor）全部存在 ✅。
- Mockup 色值：4 檔共 42 個 hex 全部對應 frontmatter token，無 spine 外的孤兒色碼 ✅。

---

## 四、Verdict

**結論：adequate → 已可交付，但仍有 1 項 high（R1 權限偏差未標註）與 3 項 medium（R2 成功狀態、R3 唯一性規則、R4 編碼壞字）需在下游 story-dev 動工前修掉；前次 48 筆 findings 修復率 33 fixed / 10 partially fixed / 5 not fixed，無倒退，且所有 token 路徑、對比值、元件名稱、流程與 mockup 色碼均已實測通過。**
