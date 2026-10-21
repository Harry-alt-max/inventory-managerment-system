- source_plan: `story-project-scaffold-plan.md`
  summary: 正式部署（waitress + build 產物）的實際啟動驗證從 story 1 縮減，改於後續 story 執行
  evidence: 使用者 2026-10-21 要求「先做 mvp、計畫縮減」；story 1 只保留設定（WhiteNoise 與 prod settings），實際以 waitress 啟動並驗證首頁可見版本字串的步驟延後
- source_plan: `_bmad-output/initiative-庫存管理系統/tickets/epic-platform-baseline/tickets/tickets.toml`
  summary: 登入失敗計數與帳號鎖定機制（連續 5 次失敗鎖 15 分鐘）延後
  evidence: 使用者 2026-10-21 決定規模縮減，主路徑只需要能登入與開單；鎖定機制屬安全強化，可在 v2 補上
- source_plan: `_bmad-output/initiative-庫存管理系統/tickets/epic-platform-baseline/tickets/tickets.toml`
  summary: 帳號生命週期（建立／停用／重設密碼）與 /admin/accounts 帳號管理頁延後
  evidence: 使用者 2026-10-21 決定規模縮減；主路徑的帳號由 seed 腳本產生即可，管理頁不是 demo 必需
- source_plan: `_bmad-output/initiative-庫存管理系統/tickets/epic-platform-baseline/tickets/tickets.toml`
  summary: 每個 epic 結尾的 Refactor sweep story 全部移除
  evidence: 使用者 2026-10-21 決定規模縮減；清理工作改為隨手進行，不單獨排 story
- source_plan: `_bmad-output/initiative-庫存管理系統/tickets/epic-stock-and-replenishment/tickets/tickets.toml`
  summary: 領用（同倉）、位置移轉、跨倉調貨單與補貨水位／待補貨清單延後
  evidence: 使用者 2026-10-21 選定「只做主路徑」＝建檔 → 入庫 → 銷貨 → 毛利查核；這四項來自簡報，其餘待主路徑可 demo 後再評估
- source_plan: `_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`
  summary: 介面英文版（en-US）翻譯延後，catalog 結構與切換骨架保留
  evidence: 使用者 2026-10-21 決定「英文介面先停用」；每個畫面維護兩份文案的成本大於收益，翻譯可日後按 catalog 逐條補
- source_plan: `_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`
  summary: 架構守門工具（import-linter／django-architectural-rules／makemigrations --check）延後至 v2
  evidence: 使用者 2026-10-21 決定規模縮減；AD-24 的規則仍以文件與 code review 維持
