---
type: epic
title: 銷售、毛利與可售查詢
parent: initiative-庫存管理系統
covers: ["R15", "R16", "R17", "R18", "R19"]
sources: ["_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md"]
after: [epic-platform-baseline, epic-item-catalog, epic-stock-and-replenishment]
refined: false
risk: high
---

# 銷售、毛利與可售查詢

## Description

銷售在成交當下完成查詢、組合、折扣與毛利試算（成本取自 E2 的批次、可用量與扣減沿用 E3 的庫存流程與調貨單、操作人員沿用 E1 的登入者機制），銷貨扣減庫存並留下可沖銷的銷貨紀錄；本 epic 只提供「建議調貨來源倉庫」的查詢輸出，調貨單的建立與移出／移入異動由 E3 執行，本 epic 不直接改動庫存。

## Outcome

銷售在報價當下就能回答「能不能賣、折多少、賺多少」，銷貨後庫存與紀錄一致、會計可查核（initiator 的 R15～R19）。

## Constraints

- 銷貨是**銷售用途扣減庫存的唯一入口**；不得以領用代替，也不得直接改寫庫存數量。
- 一張銷貨單可含多行商品，但同一商品不重複列示；可先存草稿（草稿不扣庫存）。
- 折扣為百分比、一張單僅一階、不與商品個別折扣疊加；折後金額顯示小數點後兩位。
- 成本計算基準為 FIFO：成本 = 依序消耗的批次單價 × 數量；商品無入庫成本紀錄時顯示「成本未設定」而非 0。
- 銷貨紀錄不可刪除，僅能反向沖銷（庫存回加並留下沖銷紀錄）；回退與沖銷需在同一交易內完成。

## Done when

1. 銷售查商品可見可用庫存、各倉可用量與建議調貨來源倉庫；無庫存時明確標示並給出可調貨來源。
2. 可將多項商品組成同一張銷貨單並先存草稿；草稿不扣減庫存，送出時才扣。
3. 送出後每行商品產生銷貨紀錄並扣減對應庫存，總扣減量不超過可用庫存，並各產生一筆用途＝銷貨的異動。
4. 折扣率 0～100% 可用，折後金額 = 原價合計 ×（1 − 折扣率），顯示小數點後兩位；超出範圍被拒絕。
5. 每筆銷貨即時顯示毛利與建議售價；毛利依 FIFO 結算；商品無成本紀錄時顯示「成本未設定」而非 0。
6. 銷貨紀錄含操作人員、日期、數量、金額與批次，可依日期或銷貨單號查詢；會計角色唯讀可查核。
7. 取消銷貨可回加庫存並留下沖銷紀錄，既有銷貨紀錄不被刪除。

## Boundaries

- 本 epic 屬於：銷貨單（草稿與送出）、折扣、銷貨紀錄、毛利與建議售價、可售狀態查詢、調貨來源的查詢輸出。
- 不屬於本 epic：調貨單的建立與移出／移入異動（E3）、直接改動庫存數量、領用流程（E3）、退貨流程（PRD §8.3 第 7 項，未定案）。
- 不可改變：銷貨是銷售扣減的唯一入口；跨倉異動必須有調貨單（由 E3 執行）。

## References

- parent — `_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md`，Requirements R15～R19 與 Constraints 3、4、6
- prd — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/prd-inventory-management-system.md`，§4.5 銷售與毛利、§3 毛利與批次定義
- addendum — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/addendum.md`，§D 資料庫邊界原則（交易類資料不軟刪除）

## Notes

- Decision: 2026-10-21 — 成本計算基準採 FIFO（使用者拍板）。
- Open question: 「客戶寄貨」是否視為已銷貨並計毛利（PRD §8.1 第 2 項）；折扣是否可疊加（PRD §8.1 第 3 項）— 兩者都影響本 epic 的金額公式，目前以 PRD 的暫定假設建模。
