---
name: 庫存管理系統
description: 內部進銷存後台的視覺識別契約（明亮工作台風格、倉庫琥珀配色）
type: design-spine
status: final
created: '2026-10-21'
updated: '2026-10-21'
sources: ["../prd-inventory-management-system/prd-inventory-management-system.md", "../initiative-庫存管理系統.md", "../architecture-inventory-management-system/architecture-inventory-management-system.md"]
colors:
  background: '#F6F1E7'
  background-dark: '#14100B'
  surface: '#FFFDF8'
  surface-dark: '#1D1812'
  surface-raised: '#FFFFFF'
  surface-raised-dark: '#262018'
  border: '#E0D6C2'
  border-dark: '#3A3025'
  border-strong: '#94856A'
  border-strong-dark: '#857459'
  text-primary: '#2C2620'
  text-primary-dark: '#F0E7D8'
  text-secondary: '#574E3E'
  text-secondary-dark: '#C4B7A3'
  text-muted: '#6E6553'
  text-muted-dark: '#A3967F'
  primary: '#8C4A0F'
  primary-dark: '#E09A4A'
  primary-foreground: '#FFF6E8'
  primary-foreground-dark: '#1A1209'
  primary-tint: '#F3EBE0'
  primary-tint-dark: '#33240F'
  success: '#41701F'
  success-dark: '#8FBF55'
  success-tint: '#EDF2E4'
  success-tint-dark: '#232B14'
  warning: '#8A6200'
  warning-dark: '#E0B33F'
  warning-tint: '#F7F0DF'
  warning-tint-dark: '#2E2610'
  danger: '#A33524'
  danger-dark: '#E8776A'
  danger-tint: '#F5E9E2'
  danger-tint-dark: '#331C16'
  info: '#1F6D8C'
  info-dark: '#59A8C9'
  info-tint: '#E8EEED'
  info-tint-dark: '#142A33'
  muted-tint: '#F1EDE4'
  muted-tint-dark: '#2A251C'
  accent: '#D98324'
  accent-dark: '#F0B75E'
  accent-text: '#9E5708'
  accent-text-dark: '#F0B75E'
  accent-tint: '#FBEEDD'
  accent-tint-dark: '#33240F'
typography:
  fontFamily:
    sans: "'Inter', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif"
    mono: "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace"
  fontSize:
    xs: '12px'
    sm: '13px'
    body: '14px'
    lg: '16px'
    xl: '20px'
    xxl: '26px'
  fontWeight:
    regular: '400'
    medium: '500'
    semibold: '600'
  lineHeight:
    tight: '1.35'
    normal: '1.55'
rounded:
  xs: '4px'
  sm: '6px'
  md: '12px'
  lg: '16px'
  pill: '999px'
spacing:
  base: '4px'
  scale-1: '4px'
  scale-2: '8px'
  scale-3: '12px'
  scale-4: '16px'
  scale-5: '24px'
  scale-6: '32px'
  scale-7: '48px'
  row-tight: '28px'
  row-compact: '32px'
  row-default: '40px'
  row-relaxed: '48px'
  sidebar-width: '232px'
  topbar-height: '56px'
  grid-columns: '12'
  grid-gutter: '16px'
components:
  表格:
    row-height: '{spacing.row-compact}'
    row-height-tight: '{spacing.row-tight}'
    header-height: '{spacing.row-compact}'
    cell-padding: '6px 12px'
    header-bg: '{colors.surface-raised}'
    stripe: 'rgba(140, 74, 15, 0.035)'
  卡片:
    radius: '{rounded.md}'
    shadow: '0 1px 2px rgba(44, 38, 32, 0.06), 0 4px 12px rgba(44, 38, 32, 0.05)'
    shadow-raised: '0 2px 4px rgba(44, 38, 32, 0.08), 0 12px 28px rgba(44, 38, 32, 0.08)'
    padding: '{spacing.scale-4}'
  表單:
    input-height: '36px'
    button-height: '36px'
    button-radius: '{rounded.sm}'
    input-border: '{colors.border-strong}'
    label-gap: '{spacing.scale-1}'
  焦點:
    ring: '2px solid {colors.primary}'
    offset: '2px'
  圖示:
    size-sm: '16px'
    size-md: '20px'
    stroke: '1.5px'
  版面:
    sidebar-width: '{spacing.sidebar-width}'
    topbar-height: '{spacing.topbar-height}'
    grid-columns: '{spacing.grid-columns}'
    grid-gutter: '{spacing.grid-gutter}'
---

# DESIGN.md — 庫存管理系統

視覺識別契約。本文件只管**長什麼樣**；行為與流程見 `EXPERIENCE.md`，以 `{path.to.token}` 引用本文件的 token。兩份 spine 與任何 mock、wireframe 或匯入素材衝突時，以 spine 為準。

## Brand & Style

**明亮工作台（Bright Workbench）**：溫暖、務實、清晰的後台工作介面。視覺語言取自實體庫房——牛皮紙與木箱的暖褐底色、琥珀色標示「這裡的貨的價值」、深棕文字取代冷灰。

- **出處**：此方向取自四個候選方向中的「明亮工作台」，配色取自五組候選中的「倉庫琥珀」；兩者的比較稿保留於 `.working/direction-bright-workbench.html` 與 `.working/color-themes-5.html`。
- **個性**：可靠、像櫃檯上攤開的帳冊，不像行銷網站。
- **密度**：緊湊（桌機優先）。表格列高預設 `{spacing.row-compact}`，可切 `{spacing.row-tight}`。
- **層次**：**卡片 + 細邊框 + 極輕陰影**分層，不靠重陰影或大面積色塊。
- **語氣**：介面文字是工具的用語，不是品牌的台詞；不出現標語、驚嘆號、裝飾插畫。
- **色溫**：介面整體偏暖（米白底、棕字），只有狀態色與資料本身才出現飽和色。
- **不使用**：漸層、玻璃擬態、大圓角、插畫式 icon、動畫強調字。

## Colors

語意 token 為唯一真源；元件不得直接寫入色碼。**每個色 token 皆有淺色與深色兩組值**（`-dark` 為深色對應），下表同時列出兩者。

| 語意 token | 淺色 | 深色 | 用途 |
| --- | --- | --- | --- |
| `{colors.background}` | `#F6F1E7` | `#14100B` | 應用底色 |
| `{colors.surface}` | `#FFFDF8` | `#1D1812` | 卡片、面板、表格容器 |
| `{colors.surface-raised}` | `#FFFFFF` | `#262018` | 抬升層：popover、對話框、sticky 表頭 |
| `{colors.border}` | `#E0D6C2` | `#3A3025` | **純分隔線**（表格線、區隔） |
| `{colors.border-strong}` | `#94856A` | `#857459` | **可見邊框**（輸入框、勾選框、可點擊元素），對比 ≥3:1 |
| `{colors.text-primary}` | `#2C2620` | `#F0E7D8` | 主要文字、數值 |
| `{colors.text-secondary}` | `#574E3E` | `#C4B7A3` | 標籤、次要說明 |
| `{colors.text-muted}` | `#6E6553` | `#A3967F` | 輔助文字、單位、停用與唯讀狀態 |
| `{colors.primary}` | `#8C4A0F` | `#E09A4A` | 主要動作、選取狀態、focus |
| `{colors.primary-foreground}` | `#FFF6E8` | `#1A1209` | primary 上的文字 |
| `{colors.success}` | `#41701F` | `#8FBF55` | 入庫完成、庫存充足 |
| `{colors.warning}` | `#8A6200` | `#E0B33F` | 低於水位、可用量吃緊 |
| `{colors.danger}` | `#A33524` | `#E8776A` | 庫存不足、超領、取消銷貨 |
| `{colors.info}` | `#1F6D8C` | `#59A8C9` | 跨倉調貨提示、系統訊息 |
| `{colors.accent}` | `#D98324` | `#F0B75E` | **僅非文字**：毛利強調條、進度條、圖示、選取標記 |
| `{colors.accent-text}` | `#9E5708` | `#F0B75E` | **毛利數值文字**（14px 以上亦達 4.5:1） |
| `{colors.primary-tint}` … `{colors.muted-tint}` | 見 frontmatter | 見 frontmatter | 狀態徽章底色（10% 級 tint） |

規則：

- 毛利是本系統最重要的衍生數字：數值文字用 `{colors.accent-text}`，搭配 `{typography.fontWeight.semibold}`；非文字強調（底線、進度條、圖示）用 `{colors.accent}`。**`{colors.accent}` 不得用於淺色模式的正文**（淺色下僅 2.86:1）。
- 狀態色不作為裝飾，只在語意成立時出現（低於水位＝warning、可用量不足＝danger、跨倉＝info）。
- `{colors.accent}`（琥珀）與 `{colors.warning}`（黃褐）色相接近，**兩者不得同屏近鄰使用**；摘要列的毛利強調與低於水位警示至少隔一個區塊。
- 狀態徽章一律「狀態色文字 + 對應 `-tint` 底」（如 `{colors.warning}` on `{colors.warning-tint}`，對比 ≥4.8:1）；唯讀／停用徽章用 `{colors.text-muted}` on `{colors.muted-tint}`。
- 深色模式不是把淺色反轉，而是同一組語意角色的另一組取值；任何新色都要兩套一起定義。
- 對比基準：正文 ≥4.5:1、大字 ≥3:1、非文字控制項邊框 ≥3:1。淺色與深色兩套皆須通過。

## Typography

- 字體：無襯線為主（`{typography.fontFamily.sans}`）；商品編號、批次流水號等識別碼可用等寬字（`{typography.fontFamily.mono}`）。
- 尺寸階梯：`{typography.fontSize.xs}` 12（欄位說明、單位、徽章）、`{typography.fontSize.sm}` 13（次要文字、表格次要欄）、`{typography.fontSize.body}` 14（正文、表格主欄）、`{typography.fontSize.lg}` 16（區塊標題）、`{typography.fontSize.xl}` 20（頁面標題）、`{typography.fontSize.xxl}` 26（工作台關鍵數字）。
- 字重：`{typography.fontWeight.regular}` 一般；`{typography.fontWeight.semibold}` 欄位標籤、列首、毛利數值；`{typography.fontWeight.medium}` 數值一般狀態。不依靠超過兩級的粗細差。
- 行高：表格列 `{typography.lineHeight.tight}`、內文 `{typography.lineHeight.normal}`。
- 數字與金額一律 `font-variant-numeric: tabular-nums`、右對齊、含千分位；金額固定小數兩位，數量為整數不顯示小數。
- 中英混排在排版層處理，不在字串內手動加空白。
- 不使用斜體（中文斜體不易讀）、不使用全大寫英文作為主要標題。

## Layout & Spacing

- 間距階梯以 `{spacing.base}`（4px）為基準（`{spacing.scale-1}`～`{spacing.scale-7}`）；頁面區塊之間用 `{spacing.scale-6}`，區塊內元素用 `{spacing.scale-3}`～`{spacing.scale-4}`。
- 版面骨架：左側固定導覽（`{spacing.sidebar-width}`）+ 右側主區；主區上方為頁面標題列（全域搜尋、語系切換、色彩模式、使用者選單），高度 `{spacing.topbar-height}`。
- 表格為主體時採全寬密度表格，列高 `{spacing.row-tight}`（緊湊）或 `{spacing.row-compact}`（預設）；表頭 sticky。
- 卡片內距 `{components.卡片.padding}`，卡片之間 `{spacing.scale-4}`；同一區塊的卡片以 `{spacing.grid-columns}` 欄、`{spacing.grid-gutter}` 間距排版。
- 金額、毛利等關鍵數字在摘要區右對齊，使用等寬數字，字元寬度一致因而能垂直對齊。
- 桌面優先：主要版面以 1280px 以上為設計基準；1024px 以下允許側欄摺疊為圖示列，但**不為手機重新設計**。

### 斷點行為

| 區間 | 側欄 | 表格 | 摘要列 | 目標 |
| --- | --- | --- | --- | --- |
| ≥1440px | 完整展開 `{spacing.sidebar-width}` | 全欄顯示，無橫向捲動 | 右側固定欄 | 主要開發尺寸 |
| 1280–1439px | 完整展開 | 全欄顯示，必要時橫向捲動 | 右側固定欄 | 設計基準下限 |
| 1024–1279px | 摺疊為圖示列（`{components.圖示.size-md}`） | 保留橫向捲動 | 移至表格下方，可展開 | 最小支援寬度 |
| <1024px | 同上 | 同上 | 同上 | 非主要情境，不做最佳化 |

## Elevation & Depth

- 層次只有三階：`surface`（0 階，卡片）、`surface-raised`（1 階，sticky 表頭、下拉、popover）、對話框（2 階）。
- 陰影輕量：`{components.卡片.shadow}` 用於一般卡片，`{components.卡片.shadow-raised}` 只用於浮層；不要用陰影表達「可點擊」。
- 分隔靠 `{colors.border}` 與間距，不靠陰影。
- 深色模式用**表面亮度**表達層次（background → surface → surface-raised 逐級變亮），陰影幾乎不可見，僅保留 `{colors.border}`。

## Shapes

- 圓角：輸入框與按鈕 `{rounded.sm}`、卡片 `{rounded.md}`、對話框與面板 `{rounded.lg}`、徽章與狀態點 `{rounded.pill}`。
- 表單控制項高度 `{components.表單.input-height}`／按鈕 `{components.表單.button-height}`，表格列 `{components.表格.row-height}`。
- 圖示：線性圖示，線寬 `{components.圖示.stroke}`，尺寸 `{components.圖示.size-sm}`（表格內）／`{components.圖示.size-md}`（工具列）；沿用 shadcn/ui 圖示集，不使用填充式或彩色插畫圖示。

## Components

元件名稱與 `EXPERIENCE.md` 的 Component Patterns **逐一對應**（同名同義）。標示「shadcn 預設」者表示沿用 shadcn/ui 預設行為與外觀，本 spine 不再另行約束。

| 元件 | 視覺規格 | Token 參照 |
| --- | --- | --- |
| 應用外框 | 側欄 + 頂列 + 主區；側欄選取項以 `{colors.primary}` 左側 2px 指示條 + `{colors.surface-raised}` 底 | `{spacing.sidebar-width}`、`{colors.primary}` |
| 頂列 | 高 `{spacing.topbar-height}`；左：頁面標題與說明；中：全域商品搜尋；右：語系切換、色彩模式、使用者選單 | `{components.版面.topbar-height}` |
| 側邊導覽 | 依模組分組的清單項；選取態如上；摺疊態僅留圖示 | `{colors.primary}`、`{components.圖示.size-md}` |
| 登入表單 | 置中卡片，單欄，標籤在上、錯誤在下；品牌標於卡片上方 | `{components.卡片.radius}`、`{components.表單.input-height}` |
| 資料表格 | 表頭 sticky、列高 `{components.表格.row-height}`、儲存格內距 `{components.表格.cell-padding}`、斑馬紋 `{components.表格.stripe}`、數字右對齊等寬 | `{components.表格.*}` |
| 庫存查詢列 | 表格列 + 展開的子列（子列底色 `{colors.surface-raised}`，位置代碼用等寬字） | `{colors.surface-raised}`、`{typography.fontFamily.mono}` |
| 銷貨單編輯 | 可編輯列（數量／單價／折扣輸入框）＋底部或右側的數值摘要條 | `{components.表單.input-height}` |
| 數值摘要條 | 固定條：原價合計／折扣／折後金額／毛利；毛利值用 `{colors.accent-text}` + semibold，非文字強調用 `{colors.accent}` | `{colors.accent-text}`、`{colors.accent}` |
| 位置選擇器 | 下拉／面板列出「倉庫編號 + 位置代碼 + 可用量」；不足者以 `{colors.danger}` 標示並停用 | `{colors.danger}`、`{typography.fontFamily.mono}` |
| 批次選擇器 | 清單列出批次序號、採購日期、剩餘數量、單價；預設 FIFO 建議者標「將自動選用」 | `{colors.info}`（建議標記） |
| 領用作業 | 單一表單：商品、位置、數量、用途（客戶寄貨／臨時出貨） | `{components.表單.*}` |
| 同倉移轉 | 雙欄來源／目標位置 + 數量；跨倉選項不在此畫面 | `{components.表單.*}` |
| 調貨單 | 列表 + 明細（來源倉／目標倉／商品／數量／狀態）；跨倉以 `{colors.info}` 標示 | `{colors.info}` |
| 水位設定 | 表格內可編輯整數欄位；低於水位整列以 `{colors.warning}` 標示 | `{colors.warning}`、`{colors.warning-tint}` |
| 帳號與角色 | 表格 + 抽屜編輯；角色為四選一單選 | `{components.表單.*}` |
| 表單 | 標籤在欄位上方、必填以 `*` 標示；錯誤在欄位下方用 `{colors.danger}`；提交在右下 | `{colors.danger}` |
| 狀態徽章 | 膠囊形，狀態色文字 + 對應 `-tint` 底 | `{rounded.pill}`、`{colors.*-tint}` |
| 空狀態 | 圖示 + 一句說明 + 一個主要動作按鈕 | `{colors.text-muted}` |
| 二次確認對話框 | 破壞性操作（取消銷貨、停用帳號）需明示「不可復原」與影響範圍 | `{colors.danger}` |
| 草稿提示條 | 頁面頂部的細條提示「草稿 — 尚未扣減庫存」 | `{colors.info}`、`{colors.info-tint}` |
| 骨架載入 | 表格用骨架列、卡片用骨架塊；不用全畫面轉圈 | `{colors.border}` |
| 通知計數徽章 | 頂列右側小圓點數字，無未讀時不顯示 | `{colors.danger}`、`{rounded.pill}` |
| 抽屜 | 右側滑入面板，內含標題、內容、主／次動作 | `{components.卡片.shadow-raised}` |
| 分頁器 | 表格底部右側：上一頁／下一頁／每頁筆數 | `{typography.fontSize.sm}` |
| 語系切換 | 頂列右側切換 zh-TW / en-US | `{rounded.pill}` |
| 色彩模式切換 | 頂列右側淺色／深色切換 | `{rounded.pill}` |
| 工具列與圖示 | 清單頁右上角的動作列（新增、匯出）；圖示 16/20px | `{components.圖示.*}` |

## Do's and Don'ts

**Do**

- 讓數字、編號、金額永遠等寬對齊，讓眼睛能沿著欄位垂直掃過。
- 讓顏色有意義：毛利＝`{colors.accent-text}`、低於水位＝warning、庫存不足＝danger、跨倉＝info。
- 讓表格密集但有呼吸：列高 `{spacing.row-compact}`、欄位間距 `{spacing.scale-3}`、區塊之間 `{spacing.scale-6}`。
- 讓「空狀態」教使用者下一步要做什麼。
- 讓錯誤訊息說明「發生什麼」與「怎麼修」。

**Don't**

- 不要用漸層、玻璃擬態、大面積品牌色或裝飾插畫來製造「現代感」。
- 不要用 `{colors.danger}` 呈現毛利（那是錯誤的語意）；不要用 `{colors.accent}` 呈現淺色模式的正文（對比不足）。
- 不要讓 `{colors.accent}` 與 `{colors.warning}` 在畫面上相鄰。
- 不要在表格內塞入多行文字；用 tooltip 顯示完整內容。
- 不要讓深色模式只是把淺色反轉。
- 不要為手機重新設計版面；本系統是桌機優先。
