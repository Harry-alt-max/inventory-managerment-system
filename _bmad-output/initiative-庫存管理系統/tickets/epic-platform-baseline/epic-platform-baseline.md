---
type: epic
title: 平台基線、帳號與角色權限
parent: initiative-庫存管理系統
covers: ["R1", "R2", "R3", "R20"]
sources: ["_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md"]
companions: ["_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md", "_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/DESIGN.md", "_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/EXPERIENCE.md"]
after: []
refined: true
risk: medium
---

# 平台基線、帳號與角色權限

## Description

建立專案骨架、AILearn 連線設定與資料庫 schema 基線（migration 工具），並完成後台登入、四種角色權限；同時提供操作人員（登入者）帶入機制與共用守衛規則基線（交易邊界、僅追加寫入、銷售扣減唯一入口、跨倉變動必須有調貨單），供後續庫存異動與銷貨紀錄沿用；已在本機部署環境跑通一次最小路徑。本 epic 擁有共用 setup 與共用規則，其餘 epic 只消費。

## Outcome

四種職能都能登入後台、只做自己該做的事，而且每一筆動作都記得下是誰做的——之後的庫存異動與銷貨紀錄才有可信的操作人員（initiator 的 R3）。

## Requirements

1. **登入與錯誤處理** (R1, parent R1): 使用者可用帳號密碼登入；密碼錯誤一律回應「帳號或密碼錯誤」，同一帳號連續失敗 5 次暫時鎖定 15 分鐘。
2. **角色權限** (R2, parent R2): 倉管、採購、銷售、會計四種角色各自只能存取權限表允許的畫面與操作；越權呼叫被拒絕，會計角色任何寫入都被拒絕。
3. **操作留痕** (R3, parent R3): 每筆庫存異動與每張銷貨單都帶有非空操作人員，且與登入者一致。
4. **帳號生命週期** (R20, parent R20): 可建立帳號、指派角色、停用帳號並重設密碼；停用帳號不可登入，既有紀錄保留。

## Constraints

- 參數化查詢；所有資料存取不得以字串拼接 SQL。
- 憑證由外部檔案（`pgpass.conf`）提供，程式碼、文件與版控中不得出現明文密碼；密碼單向雜湊。
- 交易邊界：造成庫存變動的寫入以交易執行，任一步失敗整筆回滾；庫存數量不得為負。
- 僅追加：交易類資料不可修改、不可刪除、不可軟刪除。
- 守衛規則：銷售用途的庫存扣減只能經由銷貨單；跨倉庫存變動必須對應一張調貨單。
- 角色固定四種不可自訂，會計為唯讀。
- 一專案一資料庫：所有資料表集中於 `AILearn`（localhost:5432），實體以關聯共存於同一 schema。
- 技術選型由架構 spine 定案：Django 6.1.2 + DRF 3.18.3 + PostgreSQL 18.6（psycopg 3.3.6）+ React 19.3.1 + Vite 8.3.4 + Tailwind + shadcn/ui；部署用 waitress + WhiteNoise。
- 介面語系為完整雙語（zh-TW 預設、en-US 次要），字串抽到 message catalog，後端錯誤以機器可讀 `code` 回應由前端本地化。

## Done when

1. 專案可在本機啟動並連上 `AILearn`，schema 由 migration 建立，憑證由 `pgpass.conf` 讀取。
2. 四種角色各有可用測試帳號；越權呼叫被拒絕並回應明確的權限錯誤，會計角色的寫入一律被拒絕。
3. 同一帳號連續 5 次密碼錯誤後暫時鎖定 15 分鐘，錯誤訊息不透露帳號是否存在。
4. 任何異動或銷貨紀錄都帶有非空操作人員，且與登入者一致。
5. 守衛規則基線可驗證：以 core 層守衛函式與測試替身驗證非銷貨單的銷售用途扣減被拒絕、無調貨單的跨倉異動被拒絕、庫存不會變負、交易中途失敗整筆回滾、交易類資料不可修改刪除；實體庫存與調貨單的驗證於 E3／E4 落實（同一套規則）。
6. 倉管可建立帳號、指派角色、停用帳號並重設密碼；停用帳號無法登入，既有紀錄保留。

## Boundaries

- 本 epic 屬於：專案骨架與部署設定、資料庫 schema 基線與 migration、登入與錯誤處理、四種角色權限、帳號生命週期、操作人員帶入機制、共用守衛規則與交易邊界基線。
- 不屬於本 epic：商品／供應商／採購批次／倉庫位置主檔（E2）、庫存異動與補貨水位（E3）、銷貨與毛利（E4）。
- 不可改變：守衛規則的行為是其他 epic 依賴的契約（銷售扣減唯一入口、跨倉必須有調貨單、僅追加、庫存不為負）。
- 觸碰點：`C:\Users\user\Desktop\pgpass.conf` — 由人維護的憑證檔，本 epic 只讀取；owner: epic-platform-baseline
- 觸碰點：`AILearn` 資料庫（localhost:5432）— schema 由本 epic 建置並擁有，其餘 epic 只消費；owner: epic-platform-baseline

## References

- parent — `_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md`，Requirements R1、R2、R3、R20 與 Constraints 1～4、6、8、9
- prd — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/prd-inventory-management-system.md`，§4.1 帳號、登入與權限、§4.6 非功能需求
- addendum — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/addendum.md`，§C 憑證與密碼處理、§D 資料庫邊界原則
- architecture — `_bmad-output/initiative-庫存管理系統/architecture-inventory-management-system/architecture-inventory-management-system.md`，AD-1～AD-7（app 邊界、依賴方向、寫入路徑、守衛規則、權限、認證、API 契約）、AD-13～AD-18（migration、測試、憑證、前端、錯誤處理、日誌）、AD-23（設定分層）、AD-24（架構守門）、AD-32（actor 契約）、AD-33（介面語系）
- design — `_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/DESIGN.md`，§ Components（登入表單、狀態徽章、表單）、§ Colors（狀態與錯誤色）
- experience — `_bmad-output/initiative-庫存管理系統/ux-inventory-management-system/EXPERIENCE.md`，§ Information Architecture（登入、頂列、側邊導覽）、§ State Patterns（登入失敗、帳號鎖定、未認證、權限不足）、§ Component Patterns（登入表單、帳號與角色）

## Notes

- Decision: 2026-10-21 — 共用守衛規則（交易邊界、僅追加、銷售扣減唯一入口、跨倉必須有調貨單）歸屬本 epic，作為其他 epic 的前置。
- Decision: 2026-10-21 — 技術選型由架構 spine 定案，本 epic 的第一個 story 不再等待未定的選型。
- Decision: 2026-10-21 — 介面語系為完整雙語，message catalog 骨架與 locale 格式化由本 epic 的前端骨架 story 一併建立。
- Decision: 2026-10-21 — 登入失敗的錯誤碼以 EXPERIENCE.md 為準：帳號不存在與密碼錯誤共用 `auth.invalid_credentials`，已鎖定為 `auth.locked`；AD-19 的「不透露帳號存在性」限指前者，架構 spine 已同步修正。
- Decision: 2026-10-21 — session 於閒置 30 分鐘後失效（無絕對期限）；過期後 `/api/v1/*` 回 401 `auth.unauthenticated`，前端導向 `/login` 並記錄 return_to。
- Decision: 2026-10-21 — 架構守門工具（import-linter／django-architectural-rules／`makemigrations --check`，AD-24）不進 E1，落地時程為 E2 起；期間規則僅存在於文件，靠 code review 維持。
- Decision: 2026-10-21 — tracer bullet 為 story 1「專案骨架與第一次連線打通」；排序為 骨架 → 登入 → 鎖定 → 權限 → 帳號生命週期 → 守衛規則基線 → 測試紀律 → Refactor sweep。
