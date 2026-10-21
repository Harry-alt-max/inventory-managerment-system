# Spine Pair Review — 庫存管理系統

受審標的：
- `DESIGN.md`（視覺 spine，type: design-spine）
- `EXPERIENCE.md`（體驗 spine，type: experience-spine）
- 驅動來源：`../../initiative-庫存管理系統.md`（Requirements R1–R20）、`../../prd-inventory-management-system/prd-inventory-management-system.md`（UJ-1～UJ-4、FR-1～FR-20、§3 Glossary）、`../../architecture-inventory-management-system/architecture-inventory-management-system.md`（AD-3、AD-6、AD-16、AD-17、AD-26）

## Overall verdict

整體為 **adequate（有條件可用）**：這對 spine 的骨架、素質與方向都成立——語意 token 架構正確、IA 與角色分流清楚、Voice and Tone 有可實作的雙語範例、UJ-1～UJ-4 完整承接 PRD 的四條旅程、mockup 自帶 `governed by` 出處註解，整體可讀性遠高於一般產出。

但作為**下游可 source-extract 的契約**還有兩道會擋住消費的缺口：一是 color token 的 YAML 路徑結構與散文引用不一致（`{colors.primary}` 對 `colors.light.primary`），嚴格解析器會解析不到任何一個顏色；二是核心數值色 `accent` 在淺色模式對比只有 2.86:1，違反 spine 自己宣告的 AA 4.5:1，而 accent 正是「毛利」這個關鍵商業數字的唯一著色。另有領用／移轉／調貨三個 R 需求完全沒有流程與行為規格、元件名稱在兩份 spine 間不對稱、與 PRD 權限表互相矛盾等高影響項目，必須在交給 architecture / story-dev 前修掉。

## 1. Flow coverage — adequate

**判斷**：UJ-1～UJ-4 四條流程結構完整（具名主角、編號步驟、標示「高潮」的節拍、UJ-1/UJ-3 有邊界路徑），且與 PRD §2.3 的 UJ 逐字對應，climax 與 PRD 的高潮定義一致。然而 R1–R20 中有 9 項在「Key Flows」層級完全缺席，其中 3 項（領用／移轉／跨倉調貨）連 Component Patterns 與 State Patterns 都沒有對應規則——這已經超出「由模式合理覆蓋」的範圍。

### Findings
- **[critical]** **R12 領用、R13 同倉移轉、R14 跨倉調貨三個核心需求既無 Key Flow 也無 Component Pattern**。IA 已列出 `/stock/issue`、`/stock/transfer`、`/stock/transfer-orders` 三個畫面（EXPERIENCE.md:51-52），但 Component Patterns（EXPERIENCE.md:112-123）沒有領用、移轉、調貨單任何一列，State Patterns（EXPERIENCE.md:127-142）也沒有對應狀態（領用用途必填、可用量不足、移轉目標位置必填、移出移入同步、跨倉必須對應調貨單）。PRD FR-14 與 initiative 約束 7「任何跨倉庫存變動都必須對應到一張調貨單」是安全攸關規則，卻沒有任何一條可被 story-dev 直接引用的行為契約。*Fix:* 至少補一條「UJ-5 倉管把貨從 B 倉移到 C 倉（跨倉調貨）」Key Flow（含失敗路徑：跨倉未開調貨單時如何阻擋），並在 Component Patterns 補「領用作業 / 同倉移轉 / 調貨單」三列。
- **[high]** **UJ-2 與 UJ-4 沒有失敗路徑**。UJ-1 有「邊界：數量或位置留空…」、UJ-3 有「邊界：若面紙只剩 C 倉有貨…」，但 UJ-2（建立採購批次）與 UJ-4（查無單號）都沒有。*Fix:* UJ-2 補「缺單價或數量時不可儲存（initiative R7）」與「同商品已有未到貨批次時提示」；UJ-4 補「查無資料時的引導與空狀態」。
- **[high]** **UJ-3 第 1 步內容自相矛盾**：搜尋「面紙」卻出現 `INV-000201 棉手套 L`（EXPERIENCE.md:197），且 UJ 標題是「賣 3 箱面紙」。這是下游最容易被直接複製成 fixture 與驗收案例的一段文字。*Fix:* 統一為同一商品（例如 `INV-000201 棉手套 L` 改名為面紙，或把搜尋字改為「手套」），並與 Voice and Tone 範例表的成功訊息（EXPERIENCE.md:95，六角螺絲）分開命名規則。
- **[medium]** **以下 6 項需求未見於任何 Key Flow，且其專屬驗收條件未寫進 Component Patterns／State Patterns**：R4（商品主檔缺必填欄位須指出哪一欄，僅由 Interaction Primitives「表單驗證」概括）、R6（供應商「同統編不得重複」無任何狀態列）、R10（倉庫編碼唯一、同倉位置代碼唯一無狀態列）、R16（同一商品不得重複出現在同一張銷貨單；架構 AD-17 已定義 `sales.duplicate_item` 錯誤碼但 spine 沒有對應 UI 狀態）、R19（銷貨單不可刪除、僅能反向沖銷；有「沖銷後」狀態但無「沖銷」這個動作的規則與入口）、R20（停用帳號不可登入、重設密碼流程無狀態列）。*Fix:* 這幾項不一定要各自成 flow，但必須在 Component Patterns 或 State Patterns 有一行可引用。
- **[medium]** **R1（登入與 5 次鎖定 15 分鐘）與 R2（越權拒絕）只以狀態形式出現，沒有流程**。目前可接受（登入不是核心旅程），但架構 AD-6 採用 session + CSRF，**session 過期（401）導向登入的行為全篇未定義**。*Fix:* State Patterns 增列「未認證（401／session 過期）：保存目前路徑並導向 /login，登入後回原頁」。
- **[low]** **R3（操作留痕）與 R5（商品查詢）僅在 UJ-1 的高潮與 mockup 中隱含涵蓋**，沒有明確的「查商品 → 看位置與數量」流程。*Fix:* 若要收斂可接受，但需在 Key Flows 開頭補一句「R3／R5 由 UJ-1 步驟 2 與 mockups/key-stock-search.html 承載」以利追溯。

## 2. Token completeness — thin

**判斷**：token 本身的定義覆蓋度不錯——14 個語意色皆有 light/dark 兩套 hex、typography 階梯完整、spacing 有 4px 基準與列高與版面尺寸、components 有卡片陰影／表格／輸入框／焦點環。但**解析結構與引用方式不匹配**，加上**對比宣告與實際數值牴觸**，且 Colors 表有重複列，consumer 端「照著 token 取值」會在第一步就失敗。

### Findings
- **[critical]** **顏色 token 的 YAML 路徑與所有散文引用不一致，嚴格 resolver 無法解析任何顏色**。frontmatter 採巢狀 `colors.light.*` / `colors.dark.*`（DESIGN.md:8-37），但全篇引用寫的是 `{colors.primary}`（DESIGN.md:116、171；EXPERIENCE.md:119、139、140、189）。design-md-spec.md 規定「The path follows the YAML structure」且 `colors` 為 flat object（`C:/Users/user/.agents/skills/bmad-ux/references/design-md-spec.md:15,43`）；shadcn 範例的寫法是 flat token + `primary-dark` 平行鍵。*Fix:* 二選一：(a) 改為 flat 鍵（`primary` / `primary-dark` / `primary-foreground` / `primary-foreground-dark`…）並同步改所有引用；(b) 保留 light/dark 巢狀但把引用改成 `{colors.light.primary}` / `{colors.dark.primary}` 並在 Colors 表明確標示每個角色的兩組路徑。目前的寫法是兩邊都不符。
- **[critical]** **`accent` 作為「毛利」文字色在淺色模式對比只有 2.86:1，違反 spine 自訂的 AA 4.5:1**。`{colors.accent}` = `#D98324` on `{colors.surface}` = `#FFFDF8` → 2.86:1（on background 更低，2.58:1）。但 Colors 表定義 accent 用途為「**毛利強調色**，僅用於毛利數值」（DESIGN.md:123），Components 表明寫「毛利值用 `{colors.accent}`」（DESIGN.md:171），而毛利是本系統最重要的衍生數字、以 14px 正文級別呈現（UJ-3 步驟 3、Step 5 高潮）。DESIGN.md:129 自己宣告「正文 4.5:1」。深色模式 `#F0B75E` on `#1D1812` = 9.77:1 通過，僅淺色模式失敗。*Fix:* 淺色 accent 至少調到 4.5:1（`#B96A0B` 級距），或明確指定 accent 僅用於大字／非文字（底色、進度條、圖示），毛利數值改用 `text-primary` + 粗體語意。
- **[high]** **警告色 `warning` 與輔助色 `text-muted` 對比不足**。`#B08000` on `#FFFDF8` = 3.48:1；狀態徽章規格為「狀態色文字 + 同色 10% 底」，實算 `#B08000` on `#F7F1DF` = **3.14:1**。`text-muted` `#8A7F6A` on surface = 3.88:1、on background = 3.50:1。兩者都低於 AA 正文 4.5:1，而 warning 承載「低於水位」這個有意義的狀態。*Fix:* 深色化 `warning` 與 `text-muted`（或規定它們只用於 ≥18.66px 粗體／圖示，列入 Do's and Don'ts）。
- **[high]** **輸入框邊框對比 1.42:1，不符合 WCAG 1.4.11 非文字對比 3:1**。`{colors.border}` `#E0D6C2` on surface = 1.42:1（深色模式 1.37:1），而 Colors 表明確指定 border 用於「**輸入框外框**」（DESIGN.md:112）。表單控制項邊框屬於 3:1 適用範圍。*Fix:* 另立 `border-strong`（如 `#B9AC95`）給輸入框／可點擊元素邊框，border 保留為純分隔線。
- **[high]** **Colors 表有重複列且該列缺色碼**。`{colors.warning}` 出現兩次，第二列的淺／深欄為 `—`、用途寫「進度條低於水位區段」（DESIGN.md:119-120）。這在 source-extract 時會造成重複鍵與缺值。*Fix:* 刪掉第二列，把「進度條低於水位區段」併進第一列的用途欄。
- **[medium]** **「唯讀」徽章的語意色 `muted` 未定義**。EXPERIENCE.md:120 寫「唯讀＝muted」，DESIGN.md:170 也把「唯讀」列為狀態徽章的用途，但 frontmatter 只有 `text-muted`，沒有 `muted` 這個色 token，也沒有「唯讀徽章用哪個 token」的約定。*Fix:* 統一改寫為 `{colors.text-muted}` 並在 Colors 表補一列「唯讀／停用」用途。
- **[medium]** **狀態徽章的 10% 底色（tint）未進 token**。DESIGN.md:170 規定「同色 10% 底」，但沒有任何 tint token；mockup 自行定義了 `--tint-primary #F3EBE0`、`--tint-success #ECF0E3`、`--tint-warning #F7F0DF`、`--tint-danger #F5E9E2`、`--tint-info #E8EEED`（mockups/key-stock-search.html 樣式區）。這是 load-bearing 的視覺值卻只存在於 mock。*Fix:* 在 `colors` 下加 `*-tint` 淺／深兩組（或新增 `tints` 區段）並在 Components 表指定各徽章 tint 來源。
- **[medium]** **無法解析的 glob 引用**：`{colors.*}`（DESIGN.md:105；EXPERIENCE.md:17,157）與 `{components.table-*}`（DESIGN.md:169）不是合法 token 路徑。*Fix:* 改為具體 token 或改寫為純文字（「語意色 token」）。
- **[low]** **未被引用的 token 與「定义了但用另一個 token 實作」的並存**：`rounded.xs`、`spacing.base`、`spacing.row-default`、`spacing.row-relaxed`、`components.card-radius`、`components.button-radius`、`components.focus-offset` 全篇未引用（其中 `card-radius`/`button-radius` 與 `{rounded.md}`/`{rounded.sm}` 語意重複），而 `{components.table-row-height}` 與 `{spacing.row-compact}` 是同一個值的兩個名稱。*Fix:* 刪除冗餘鍵，或在 frontmatter 註明別名關係。

## 3. Component coverage — thin

**判斷**：兩份 spine 各有一張元件表，但**兩邊的名字集合幾乎不重疊**——19 個具名元件中只有 4 個（資料表格、狀態徽章、二次確認對話框、語系切換）同時有視覺列與行為列。視覺側缺 6 個、行為側缺 5 個。此外至少有 8 個在兩份 spine 內被具名使用的元件（抽屜、分頁器、提示條、骨架載入、通知計數徽章、工具列、圖示、登入表單）在兩張表中都沒有列。

### Findings
- **[high]** **視覺側缺列（EXPERIENCE 有名字、DESIGN 無規格）**：庫存查詢列、銷貨單編輯、位置選擇器、批次選擇器、水位設定、帳號與角色（EXPERIENCE.md:114-122）。其中位置選擇器與批次選擇器是本系統最具特色、也最難臨時決定的元件（EXPERIENCE.md:117-118 描述了內容量、可用性、FIFO 標示），下游沒有任何視覺依據可依。*Fix:* 在 DESIGN.md Components 補這 6 列的視覺規格（色彩 token、密度、尺寸、狀態外觀）。
- **[high]** **行為側缺列（DESIGN 有名字、EXPERIENCE 無規則）**：應用外框、頂列、數值摘要條、表單、空狀態（DESIGN.md:167-173）。*Fix:* 在 EXPERIENCE.md Component Patterns 補這 5 列的互動規則（外框的導覽展開/選取、頂列搜尋與選單、表單驗證與儲存、空狀態的主動作、摘要條的即時重算與鍵盤操作）。
- **[high]** **被具名使用但兩表皆無列的元件**：抽屜（UJ-2 步驟 3、帳號與角色「表格 + 抽屜編輯」）、分頁器（Interaction Primitives 分頁）、草稿提示條（State Patterns 草稿）、骨架（State Patterns 載入中）、通知計數徽章（IA 通知列）、工具列與圖示（Shapes 提及 20px 工具列圖示）、登入表單（IA `/login`）。*Fix:* 為每一個補列，或明確標示「沿用 shadcn/ui 預設，不受本 spine 約束」。
- **[medium]** **同一元件跨表名稱漂移**：DESIGN「數值摘要條」vs EXPERIENCE「摘要條」「摘要區」（DESIGN.md:171；EXPERIENCE.md:116,136,149,200）；DESIGN 表頭用「元件」、EXPERIENCE 用「Pattern」。*Fix:* 統一元件名（建議全用「元件」），並在兩份 spine 的元件表互相列出對應名稱。
- **[medium]** **語系切換與色彩模式在兩個位置同時出現**。DESIGN.md:168 與 EXPERIENCE.md:31 都把「語系切換、色彩模式」放在頂列右側，但導覽規則（EXPERIENCE.md:67）又說「使用者選單永遠顯示：姓名、角色、語系切換、色彩模式、登出」。*Fix:* 指定唯一權威位置（建議頂列），使用者選單只留姓名／角色／登出。

## 4. State coverage — thin

**判斷**：State Patterns 有 14 列且覆蓋了常見的載入／空／無結果／權限不足／登入失敗／草稿／提交後／沖銷後／成本未設定／可用量不足／負毛利／批次不足／語系，方向正確。但它是以「狀態」為軸而非以「畫面」為軸，導致 IA 中 3 個畫面（領用、移轉、調貨單）完全沒有狀態，且數個需求專屬的錯誤狀態缺席。

### Findings
- **[high]** **IA 中 3 個畫面零狀態規格**：`/stock/issue`（用途必填且限定「客戶寄貨／臨時出貨」、不可超可用量、領用不計毛利）、`/stock/transfer`（目標位置必填、限同倉、移出移入同步、總量不變）、`/stock/transfer-orders`（跨倉、移出移入兩筆異動、必須可回溯調貨單）（EXPERIENCE.md:51-52；狀態表 EXPR:127-142 皆無）。*Fix:* 每一個畫面至少補「成功」「可用量不足」「欄位缺漏」「跨倉被擋」四類。
- **[high]** **需求專屬的錯誤狀態缺席**：供應商「同統編不得重複」（initiative R6／PRD FR-7）無狀態列；銷貨單「同一商品不重複」（R16，架構 AD-17 已有 `sales.duplicate_item` 錯誤碼）無狀態列；帳號「停用帳號不可登入」與「重設密碼」（R20）無狀態列；「批次流水號 `PO-YYYYMMDD-序號`」與「倉庫編碼／同倉位置代碼唯一」（R7、R10）無驗證規則。*Fix:* 每一項錯誤碼／唯一性規則都應有一列 State Pattern（沿用架構 AD-17 的機器可讀 `code` 名稱最利於下游對接）。
- **[medium]** **未認證（401／session 過期）未定義**。架構 AD-6 用 Django session + CSRF，spine 未說明 session 過期時導向登入、是否保留原路徑。*Fix:* 增列「未認證：導向 /login 並記錄 return_to」。
- **[medium]** **「通知」是全域列但沒有目的地**。IA 通知列路由寫「全域」（EXPERIENCE.md:32），模組與畫面表沒有通知中心畫面，也沒有「計數徽章 = 0」的呈現與點擊後去向。*Fix:* 要嘛指定 `/notifications` 畫面與其狀態，要嘛明示通知僅為指標不需落地頁。
- **[medium]** **「權限不足」有兩套互斥規則**。導覽規則說「無權限的項目不顯示，而不是顯示成停用狀態」（EXPERIENCE.md:66），State Patterns 卻說「403 畫面說明『這個功能需要 XX 角色』」（EXPERIENCE.md:132）。*Fix:* 明確定義兩種情境：導覽層隱藏 vs 直接輸入越權 URL／API 403 顯示 403 畫面。
- **[low]** **空狀態的內容規範只寫在元件表**：State Patterns 的「空資料」列（EXPERIENCE.md:130）與 Voice and Tone 的「空狀態」列（EXPERIENCE.md:80）重述同一規則但未統一用語（「查無資料」是禁止寫法）。*Fix:* 合併為一條規範。

## 5. Visual reference coverage — adequate

**判斷**：mockups/ 底下 4 個檔案**全部**有被引用，無孤兒檔案；每個檔案都在「視覺參考」表列出並標明涵蓋的 spine 章節，mockup 本身還帶有逐條 `governed by` 註解指向 spine 章節，來源可追溯性是這對 spine 的強項。缺的是「inline」這件事本身。

### Findings
- **[medium]** **引用集中在單一「視覺參考」表，沒有在相關章節 inline 連結**。IA（EXPERIENCE.md:23-68）、Component Patterns（:110-123）、State Patterns（:125-142）、Key Flows 各處都沒有指向 mockup 的連結；範例檔（experience-example-shadcn.md:29）是在 IA 段落尾端以「→ Composition reference: …」inline 引用。*Fix:* 在 IA 段落與 Key Flow 內各加一行 inline 連結到對應 mockup。DESIGN.md 也完全沒有引用任何 mockup，視覺契約與視覺基準脫節。
- **[medium]** **mockup 含 spine 未承諾的色值**。除 14 個語意色外，四個 mockup 共用了 `#CFC5B0`、`#EDE5D6`、`#F3EBE0`、`#F5E9E2`、`#F7F0DF`、`#E8EEED`、`#ECF0E3`，以及深色用的 `#302517`、`#302716`、`#31211B`、`#4A3F2F`、`#CFC5B0`（推導自語意色但未入 token）。Spine 明訂「語意 token 為唯一真源」（DESIGN.md:105），但 mockup 實際用到的 tint 未進 token——這與第 2 節的 tint 缺口是同一個問題的兩面。*Fix:* 見第 2 節 tint token 建議。
- **[medium]** **IA 有 17 個模組畫面，mockup 只涵蓋 4 個**，且「視覺參考」未說明其餘畫面是否有意不產出。*Fix:* 補一句「其餘畫面尚無 1:1 mockup，視覺基準由 DESIGN.md 承載」。
- **[low]** **`.working/` 下的 4 個 direction 與 5 個 color theme 未被任何 spine 引用**（`direction-bright-workbench.html`、`color-themes-5.html` 等）。Brand & Style 的「明亮工作台」決策沒有任何出處，讀者無法得知它是四個方向中擇一。*Fix:* 在 DESIGN.md Brand & Style 加上「取自 .working/direction-bright-workbench.html／color-themes-5.html 的 X 方案」一行。

## 6. Bloat & overspecification — adequate

**判斷**：整體克制，沒有明顯灌水。DESIGN.md 192 行、EXPERIENCE.md 217 行，密度合理，沒有整節屬於「沒有下游會讀」的內容。主要問題反過來是**欠規格**：有幾處 pixel 值出現在 token 該覆蓋的地方，卻沒有對應 token。

### Findings
- **[medium]** **「28px 緊湊列」是孤立的 pixel 規格，沒有 token**。Brand & Style（DESIGN.md:97）與 Layout & Spacing（:145）都說「可切換 28px 緊湊列」，但 spacing 裡只有 `row-compact: 32px`、`row-default: 40px`、`row-relaxed: 48px`，沒有 28px 對應鍵；且 28px 低於 32px 基準，與「間距階梯以 4px 為基準」相衝突。mockup 也實際用到 28px。*Fix:* 新增 `spacing.row-tight: '28px'`（或把 compact 定為 28、default 定為 32）並讓敘述改引用 token。
- **[medium]** **圖示規格沒有 token**。「1.5px 線寬的線性圖示、尺寸 16px／20px」（DESIGN.md:161）是無 token 依據的 pixel 規格，且未指明圖示套件。*Fix:* 新增 `icon.size-sm / size-md / stroke` token。
- **[medium]** **「同一區塊的卡片以 12 欄格概念排版」未定義 grid token**（DESIGN.md:146），且「1 位元組的空間」疑似誤植（DESIGN.md:147，應為「1 個字元寬」）。*Fix:* 定義 `spacing.grid-columns: 12` 與 `spacing.grid-gutter`，並修正誤植。
- **[low]** **Do's and Don'ts 重述 token 數值**（列高 32px、欄位間距 12px、區塊之間 32px，DESIGN.md:182）。*Fix:* 改為引用 token 或刪除數值，避免雙份真相。
- **[low]** **「非目標（UX 層）」逐條重述 PRD §5／§6.2 與 initiative Boundaries**（EXPERIENCE.md:212-217），對下游 story-dev 沒有新增資訊。*Fix:* 保留一條指向 PRD 的連結即可。
- **[low]** **少數語句贅詞**：「緊湊（緊湊密度，桌機優先）」（DESIGN.md:97）、「集合」等。*Fix:* 潤稿時一併收斂。

## 7. Inheritance discipline — thin

**判斷**：跨文件命名大致穩定（两份 spine 的 `name` 一致為「庫存管理系統」，IA 模組標註 E1–E4 對齊 ticket epic，UJ 名稱與 PRD 逐字相符），但來源追溯、顏色路徑、元件名稱三處不嚴謹；且 Foundation 把一項架構 spine 沒有的技術決策掛在 AD-16 名下。

### Findings
- **[high]** **兩份 spine 都沒有 `sources` frontmatter**（DESIGN.md:1-6、EXPERIENCE.md:1-7），無法解析、也無追溯路徑。相較範例檔（experience-example-shadcn.md:4-5 有 `sources:` 指向 PRD）與本專案其他 artifact（initiative、architecture、PRD 皆有 `sources`），這裡是明顯缺口。*Fix:* DESIGN.md 與 EXPERIENCE.md 皆補 `sources:`，分別指向 `../prd-inventory-management-system/prd-inventory-management-system.md` 與 `../initiative-庫存管理系統.md`（並註明 mockups/ 為視覺基準）。
- **[high]** **Foundation 把 shadcn/ui + Tailwind 掛在 AD-16 名下，但 AD-16 並未包含它**。EXPERIENCE.md:16 寫「（來自架構 spine AD-16）：React 19 + TypeScript + Vite 的單頁應用，以 shadcn/ui + Tailwind CSS 為元件基礎；後端 DRF，認證為 session + CSRF（同源）」；實際 AD-16 只規定「前端為 Vite + React + TypeScript…由 Django（WhiteNoise）同源供應」（architecture:137），session + CSRF 是 AD-6（architecture:73-77），而 shadcn/ui + Tailwind 在整份架構 spine 中**完全沒有出現**（已全文搜尋確認）。這代表 UI 元件庫是一個未經架構拍板的隱性決策。*Fix:* 改寫為分別引用 AD-16（前端建置）與 AD-6（認證），並把 shadcn/ui + Tailwind 明確標為「本 UX spine 提出的 UI 層決策，待架構/開發確認」。
- **[high]** **IA 的角色表與 PRD FR-2 權限表互相矛盾**。EXPERIENCE.md:52 把「調貨單（跨倉）」主要角色列為「倉管、銷售」，但 PRD FR-2 權限表（prd:85）「銷貨單與調貨單」只有銷售有權、倉管為「—」；EXPERIENCE.md:58 把「待補貨清單」主要角色只列採購，但 PRD 允許銷售（唯讀）與會計（唯讀）（prd:84）。下游若照 EXPERIENCE.md 實作角色閘門會與 PRD 驗收衝突。*Fix:* 依 PRD FR-2 重整「主要角色」欄，區分「可操作／唯讀可見」。
- **[medium]** **EXPERIENCE.md 的 token 引用名稱全部能在 DESIGN.md 找到**（`{colors.danger}`、`{colors.surface-raised}`、`{colors.warning}`、`{components.focus-ring}`、`{components.table-row-height}`、`{typography.font-mono}`、`{typography.number-font}`）——這部分通過。問題在於顏色那三個依第 2 節的巢狀結構無法解析。
- **[medium]** **專有名詞與 PRD Glossary 不完全一致**。PRD §3 的「庫存位置（Location）」「庫存異動」「調貨單」「領用用途」「水位」在 spine 中被改稱／混用：EXPERIENCE.md 用「庫存位置」正確，但 UI 層用「位置」／「位置代碼」、DESIGN.md 用「選取項」等；「庫存異動」在 spine 中寫成「異動」／「庫存異動」兩種（「庫存異動紀錄」路由、`/stock/movements`）。*Fix:* 建立一份兩份 spine 共用的術語對照（引用 PRD §3 定義），尤其「庫存異動」「庫存位置」「調貨單」。
- **[medium]** **`muted` vs `text-muted`、`摘要條` vs `數值摘要條` 的名稱不一致**（見第 2、3 節）。*Fix:* 同上。
- **[medium]** **`accent` 與 `warning` 語意撞色**。Do's and Don'ts 說「毛利＝琥珀、低於水位＝琥珀黃」（DESIGN.md:181），但 accent `#D98324` 與 warning `#B08000` 同屬琥珀色系，深色模式 `#F0B75E` vs `#E0B33F` 幾乎難以分辨，而 accent 是「唯一用於毛利」的專屬色。*Fix:* 讓 accent 與 warning 在色相上明顯分離（例如 accent 偏綠銅色），或在 Colors 表註明兩者不得同屏近鄰使用。
- **[low]** **DESIGN.md frontmatter 缺 `description`**（design-md-spec.md:14 列為標準欄位，shadcn 範例亦有）。*Fix:* 補一行 `description: 內部進銷存後台的視覺識別契約（明亮工作台風格）。`

## 8. Shape fit — adequate

**判斷**：DESIGN.md 章節順序完全符合 canonical 順序；EXPERIENCE.md 的必要章節全部到位，Responsive & Platform 這一節在這個專案是**成立的**（不是冗餘），因為專案確實宣告了 1024px 的折疊行為與桌機優先的產品邊界。

### Findings
- **[low]** **DESIGN.md 章節順序正確**：Brand & Style → Colors → Typography → Layout & Spacing → Elevation & Depth → Shapes → Components → Do's and Don'ts（DESIGN.md:92,103,131,141,150,157,163,177），完全符合 design-md-spec.md 的 order-locked 規範。**EXPERIENCE.md 必要章節齊備**：Foundation、Information Architecture、Voice and Tone、Component Patterns、State Patterns、Interaction Primitives、Accessibility Floor、Responsive & Platform、Key Flows 皆在，另加「視覺參考」與「非目標（UX 層）」。
- **[medium]** **Responsive & Platform 節是合理的，但覆蓋度不足**。該節已宣告 1280px 基準／1440px 主要開發尺寸／1024px 以下側欄摺疊／不做手機專屬版面／目標環境 Windows Chrome+Edge（EXPERIENCE.md:165-170），與 DESIGN.md:148 的 1024px 敘述一致——因此保留該節是對的。*但*未給出 1440px 以上（寬螢幕）與 1024–1280px 兩個區間的具體行為，且 1024px 折疊後「摘要條改為可展開的底部列」在 DESIGN.md 沒有對應的視覺規格。*Fix:* 補一張 breakpoint 行為表（對齊範例檔的三列寫法），並在 DESIGN.md 補折疊側欄的視覺規格。
- **[low]** **兩份 spine 都沒有 IA 示意圖**（Mermaid 或其他）。範例檔也沒有，故非硬性缺失；但本專案的 IA 有 5 模組 / 17 畫面與角色落地分流，一張圖能顯著降低下游誤讀。*Fix:* 選用（機械檢查未發現任何 Mermaid 語法錯誤，因全篇無 Mermaid）。
- **[low]** **EXPERIENCE.md 缺「Inspiration & Anti-patterns」節**（範例檔有）。本專案已有「非目標（UX 層）」與 DESIGN.md 的 Do's and Don'ts 補足，但「被拒絕的設計方向」目前只散落在 mockup 的註解中。*Fix:* 選用，把 `.working/` 中被捨棄的方向整理成一節。

## Mechanical notes

**名稱不一致**
- `accent` / `warning` 語意撞色（見第 7 節）；`muted`（EXPERIENCE.md:120）vs `text-muted`（frontmatter）。
- 「數值摘要條」（DESIGN.md:171）vs「摘要條」「摘要區」（EXPERIENCE.md:116,136,149,200）。
- DESIGN.md 元件表欄名「元件」vs EXPERIENCE.md「Pattern」。
- 「異動」vs「庫存異動」；「位置」vs「庫存位置」。
- Frontmatter `components` 鍵為 `card-radius` / `focus-ring` / `table-row-height` 等「屬性名」而非元件名，與 design-md-spec.md:19「Component-name → object of component tokens」不符（值為純量而非物件）。下游若依 spec 期待 `components.<元件名>.<屬性>` 的結構會讀不到。

**斷鏈／無法解析的引用**
- `{colors.primary}` 等 15 個顏色引用 vs 巢狀 `colors.light/dark`（第 2 節，critical）。
- `{colors.*}`（DESIGN.md:105；EXPERIENCE.md:17,157）與 `{components.table-*}`（DESIGN.md:169）為 glob，非合法 token 路徑。
- `{path.to.token}`（EXPERIENCE.md:11）為說明性佔位符，非實際引用，無害。
- 兩份 spine 皆無 `sources`（第 7 節）。
- `mockups/` 連結為相對路徑 `mockups/key-login.html`，相對於 spine 檔案位置正確，可解析。

**Frontmatter 完整性**
- DESIGN.md：`name` ✅、`description` ❌（缺）、`colors` ⚠（巢狀結構與引用不符）、`typography` ✅（但型別是字串而非 spec 要求的 `fontFamily`/`fontSize`/`fontWeight`/`lineHeight` 物件）、`rounded` ✅、`spacing` ✅、`components` ⚠（純量非物件、鍵非元件名）。另含非標準鍵 `type` / `status` / `created` / `updated`（無害，且與本專案其他 artifact 一致）。
- EXPERIENCE.md：缺 `sources`；`type`/`status`/`created`/`updated` 為非標準鍵但與其他 artifact 一致。

**字面／文字層**
- DESIGN.md:147「以 1 位元組的空間與其他數字對齊」語意不通（應為「1 個字元寬」）。
- DESIGN.md:120 為 `{colors.warning}` 的重複列且值為 `—`（見第 2 節）。
- EXPERIENCE.md:197 搜尋「面紙」對應到「棉手套」（見第 1 節）。
- EXPERIENCE.md:95 的雙語成功訊息中，en-US 版本保留中文「B 倉 A-03」（倉名／位置代碼為資料不隨語系改變，與 EXPR:142 一致，屬合理但未加註，可能被誤讀為漏翻）。
- EXPERIENCE.md:97「中文句末不加句號的短標籤除外，一律使用全形標點」語序易誤讀。

**Mermaid 語法**
- 兩份 spine 皆未使用 Mermaid，無語法錯誤可檢。

**跨文件一致性抽樣**
- 架構 spine 的 AD-17 定義了機器可讀錯誤碼（`stock.insufficient`、`auth.locked`、`sales.duplicate_item`），EXPERIENCE.md 的 State Patterns 未使用任何一個錯誤碼名稱；下游若要對接錯誤包絡（AD-7）會失去對齊點。建議 State Patterns 直接引用這些 `code`。
- 架構 spine AD-15 規定「明文密碼不得出現在任何文件」，本 spine 與 mockup 均未出現憑證，✅ 通過。
