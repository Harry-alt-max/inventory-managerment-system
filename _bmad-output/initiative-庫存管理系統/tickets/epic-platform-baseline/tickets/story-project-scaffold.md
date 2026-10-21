---
id: 1
type: story
title: "專案骨架與第一次連線打通"
parent: epic-platform-baseline
after: []
hitl: true
risk: medium
---

# 專案骨架與第一次連線打通

## Description

建立 Django 專案與四層 settings（base／dev／test／prod，prod 缺 SECRET_KEY 或允許主機即啟動失敗）、以 PGPASSFILE 連 AILearn、第一組 migration、core/exceptions.py 與單一 DRF exception handler（錯誤一律回 {code, detail, field_errors}）、/api/v1/health 端點、Vite + React + TS + Tailwind + shadcn 前端骨架與應用外框（側欄依角色顯隱、頂列含語系切換與使用者選單、登出）、以 zh-TW／en-US 起步的 message catalog、WhiteNoise 靜態檔與 waitress 啟動方式；所有資料存取以參數化查詢書寫。

## Requirements

Verify: 開發者啟動後端與前端後，開啟前端首頁可看到後端回應的版本字串，切換語系會改變畫面文字；改以 waitress 啟動並 build 前端後開啟首頁，同樣看得到版本字串。

## References

- parent — `_bmad-output/initiative-庫存管理系統/tickets/epic-platform-baseline/epic-platform-baseline.md`，Description、Constraints、Done when
- architecture — `_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`，AD-1（app 邊界）、AD-2（依賴方向）、AD-3（寫入路徑）、AD-7（API 契約與錯誤包絡）、AD-13（migration）、AD-15（資料庫與憑證）、AD-16（前端建置與供應）、AD-17（錯誤處理集中）、AD-23（設定分層與環境分離）、AD-33（介面語系）、§ Stack（版本）、§ Structural Seed（原始碼樹、環境表）
- design — `_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/DESIGN.md`，§ Colors、§ Typography、§ Components（應用外框、頂列、側邊導覽、狀態徽章）
- experience — `_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/EXPERIENCE.md`，§ Foundation、§ Information Architecture（頂列、側邊導覽、全域框架）、§ Voice and Tone、§ Accessibility Floor

## Notes

- hitl（由人執行的部分）：建立 Python 虛擬環境、安裝前後端依賴、啟動後端與前端、開發資料庫 migration 套用。本 story 的程式碼部分（專案結構、設定、端點、前端骨架）由開發者完成。
- 本 story 不含架構守門工具（import-linter／django-architectural-rules／`makemigrations --check`，AD-24）：使用者於 2026-10-21 決定其落地時程為 E2 起。
- 密碼與憑證：一律不寫入程式碼或文件，連線憑證由 `PGPASSFILE` 指向的 `pgpass.conf` 提供（AD-15）。
- 前端資料層與快取方案尚未選定（架構 spine 的 Open Questions），本 story 只建立骨架與 message catalog 骨架，方案由後續 story 決定。
