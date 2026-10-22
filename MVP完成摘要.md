# MVP 完成摘要

## 📅 完成日期：2026-10-22

## 目標概述
完成角色-based login（帳號密碼 + 職能快速選擇）與 MVP 主路徑：商品主檔 → 批次 → 位置 → 入庫 → 銷貨 → 毛利查核。

---

## ✅ 已完成項目

### 1. 告知：帳號密碼登入回來
- 登入頁恢復帳號+密碼表單（`測試帳號.md` 的四組帳密有效）
- 底部留連結「或直接選擇職能進入（示範模式）」
- 兩種方式都能用：傳統密碼登入或快速選職能（`DEMO_ROLE_LOGIN=True`）

### 2. MVP 主路徑實測通過
完整流程：

```
建商品 → 建批次 → 建倉庫/位置 → 入庫 100 → 開單賣 30（9折）→ 毛利查核
```

| 項目 | 金額 | 備註 |
|------|------|------|
| 原價合計 | 600.00（30 × 20.00） | 售價 × 數量 |
| 折後金額 | 540.00（9 折） | 整單折扣 10% |
| 成本合計 | 360.00（30 × 12.00，FIFO） | 依入庫時間先扣舊批次 |
| **毛利** | **180.00** | 折後金額 − 成本 |

- 銷貨單號 `SO-20261022-001`
- 庫存 100 → 70（送出後扣減）
- 批次消耗明細與庫存異動均留存
- 會計帳號查得到毛利但不可建立銷貨單

### 3. 前端介面
- **側邊導覽**：新增「銷貨」（銷售角色）與「毛利查核」（銷售、會計角色）
- **開單頁**：選商品 → 選位置 → 數量、售價 → 加入多列 → 填整單折扣 → **試算毛利**（原價/折扣/折後/成本/毛利五欄）→ **建立並送出**
- **毛利查核頁**：依日期或單號查每筆銷貨的折後金額、成本、毛利（唯讀）

### 4. 後端服務
- **sales app**（新增：models、services、views、urls）
- 模型：`SalesOrder`、`SalesOrderLine`、`BatchConsumption`
- 服務：`quote()`（試算、不寫入）、`create_order()`、`submit_order()`、`reverse_order()`、`list_orders()`
- 成本採用 **FIFO**（依批次入庫時間順序消耗）
- 整單折扣：單一百分比適用於全部
- 毛利定義：`折後金額 − 成本`
- 送出與沖銷皆在 **同一交易** 內更新庫存與寫入異動

### 5. 測試
- **48 個後端測試全過**（新增 8 個銷貨測試）
- 測試覆蓋：草稿不動庫存、送出扣庫存留異動、FIFO 先扣舊批次、毛利公式、超量拒絕、重複商品拒絕、沖銷回加、會計唯讀不可寫

---

## 🗂️ 結構變更

### 新增檔案
| 路徑 | 說明 |
|------|------|
| `backend/sales/__init__.py` | app 初始化 |
| `backend/sales/apps.py` | AppConfig |
| `backend/sales/models.py` | SalesOrder / SalesOrderLine / BatchConsumption |
| `backend/sales/services.py` | 核心業務服務（quote / create / submit / reverse） |
| `backend/sales/views.py` | DRF API 視圖（quote、list、detail、submit、reverse、margins） |
| `backend/sales/urls.py` | URL 設定（/api/v1/sales/*） |
| `backend/tests/test_sales.py` | 8 個新增測試 |
| `frontend/src/pages/SalesPage.tsx` | 開單頁（React + TanStack Query） |
| `frontend/src/pages/MarginPage.tsx` | 毛利查核頁 |
| `frontend/src/lib/api.ts` | API 客製函數（quoteOrder、createSalesOrder 等） |
| `frontend/src/i18n/catalog.ts` | i18n 字串（中文+英文） |
| `frontend/src/features/shell/nav-items.ts` | 導覽項目（銷貨、毛利查核） |
| `frontend/src/App.tsx` | 路由與登入頁恢復（帳密 + 職能快速選擇） |
| `frontend/src/pages/LoginPage.tsx` | 登入頁（onPickRole 參數） |

### 修改檔案
| 路徑 | 說明 |
|------|------|
| `backend/sales/services.py` | submit_order 重算 FIFO 成本與消耗 |
| `backend/sales/views.py` | 串接模型欄位 total_discount / total_paid 等 |
| `backend/stock/models.py` | 新增 PURPOSE_SALE / PURPOSE_SALE_REVERSAL 到 StockMovement.PURPOSE_CHOICES |
| `backend/config/settings/base.py` | 加入 "sales" app |
| `backend/core/urls.py` | 加入 /sales/ 路由 |
| `frontend/src/i18n/catalog.ts` | 新增所有 sales / margins / nav 字串 |
| `README.md` | 僅文字說明更新 |

---

## 🔢 關鍵決策（AD 參考）

| 規則 ID | 說明 |
|---------|------|
| AD-8 | 序列生成：PO 號、銷貨單號 `SO-YYYYMMDD-NNN` |
| AD-9 | 金額一律小數兩位、ROUND_HALF_UP |
| AD-11 | 成本 FIFO：依入庫時間順序 |
| AD-18 | 毛利 = 折後金額 − 成本 |
| AD-22 | 同一張單同一商品/位置不可重複 |
| AD-26 | 報價試算不寫入任何資料 |
| AD-28 | 送出與沖銷在同一交易內更新庫存、留下異動 |
| AD-29 | StockLevel 單一來源真相 |
| AD-31 | 批次消耗明細（PO number、quantity、unit_price、cost） |
| AD-33 | 錯誤包絡 `{code, detail, field_errors}` |
| AD-5 | 權限：銷售=create/view_sales_order、會計=view_margin 唯讀 |

---

## 📦 測試帳號（`測試帳號.md`）

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 管倉 | `demo_warehouse` | `tyuismq5bp7u` |
| 採購 | `demo_purchasing` | `va6pvyydchqv` |
| 銷售 | `demo_sales` | `v5ndqwfadcd7` |
| 會計 | `demo_accounting` | `8xnn56jgcafu` |

---

## ⏭️ 後續（v2，記在 `deferred-work.md`）

- 銷貨單列表頁（分頁、匯出）
- 折扣金額實際扣除確認
- 毛利查核匯出（CSV/Excel）
- 倉庫與位置 UI 介面（讓作業全程用滑鼠）
- 領用、移轉、跨倉調貨、待補貨清單
- 帳號管理頁

---

## 🛠️ 開發指令

```powershell
# 啟動系統（如果尚未開啟）
cd C:\Users\user\Desktop\庫存管理系統
.\啟動系統.bat

# 開啟瀏覽器
# <http://127.0.0.1:5173>

# 停止系統
.\停止系統.bat

# 執行後端測試
cd backend
$env:PGPASSFILE = "C:\Users\user\Desktop\pgpass.conf"
& .\.venv\Scripts\python.exe -m pytest
```

---

**狀態：MVP 完成。48 個後端測試全部通過，端對端實測主路徑驗收無誤。**