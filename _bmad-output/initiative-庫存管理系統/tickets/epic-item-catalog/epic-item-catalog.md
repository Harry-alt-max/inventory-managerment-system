---
type: epic
title: 商品、供應商、倉庫位置與採購批次
parent: initiative-庫存管理系統
covers: ["R4", "R7", "R9", "R10"]
sources: ["_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md"]
after: [epic-platform-baseline]
refined: false
risk: low
---

# 商品、供應商、倉庫位置與採購批次

## Description

商品、供應商、倉庫與位置、採購批次都可建檔與查詢（受 E1 的登入與角色權限控管），並提供名稱查詢索引、批次成本與建議售價給入庫（E3）與銷售（E4）引用；商品主檔預留可空的水位欄位。

## Outcome

倉管與採購能把商品與其成本、供應商、存放位置建進系統，之後入庫與銷售有可引用的成本與位置依據（initiator 的 R4、R7、R9、R10）。

## Constraints

- 同一統編只允許一筆供應商資料；同倉庫內位置代碼唯一。
- 採購批次流水號格式 `PO-YYYYMMDD-序號`，序號在同一天內全域遞增、不重複。
- 總價由單價 × 數量自動計算，不另外輸入。
- 庫存數量、批次與採購單價**不由商品建檔填寫**，一律由採購批次與入庫帶入，避免同一資料有兩個來源。
- 成本計算基準已定為 FIFO：批次層級的單價與數量足以支撐 FIFO 結算，本 epic 只負責保存批次原始資料，結算由 E3／E4 使用。

## Done when

1. 倉管建立商品後取得 `INV-` + 6 碼的系統編號；缺名稱或供應商時被擋下並指出缺哪一欄。
2. 採購建立含統編、公司名稱、聯絡人、電話的供應商；同統編重複建立時被拒絕並指向既有資料。
3. 採購建立採購批次後，總價等於單價 × 數量，缺單價或數量時不可儲存，同日流水號不重複。
4. 倉管建立倉庫（唯一編碼）與其下位置；同倉重複位置代碼被拒絕。
5. 依名稱部分關鍵字可找到商品並顯示主檔欄位（庫存現況與位置數量由 E3 補上）。
6. 商品主檔具可空的水位欄位，尚未設定時不列入任何清單。
7. 帳號生命週期由 E1 提供：只有被授權的角色能建檔，越權建檔被拒絕。

## Boundaries

- 本 epic 屬於：商品主檔與名稱查詢索引、供應商資料、採購批次、倉庫與庫存位置、商品主檔的水位欄位。
- 不屬於本 epic：庫存現況與入庫／領用／移轉／調貨（E3）、銷貨與毛利（E4）、商品查詢中的庫存數量與位置數量（E3，資料此時尚未存在）。
- 不可改變：批次層級的單價與數量必須原樣保存，成本基準（FIFO）不得在此被改寫成彙總值。

## References

- parent — `_bmad-output/initiative-庫存管理系統/initiative-庫存管理系統.md`，Requirements R4、R7、R9、R10 與 Constraint 9
- prd — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/prd-inventory-management-system.md`，§4.2 商品與批次、§4.3 供應商與採購
- addendum — `_bmad-output/initiative-庫存管理系統/prd-inventory-management-system/addendum.md`，§D 資料庫邊界原則

## Notes

- Decision: 2026-10-21 — 成本計算基準採 FIFO（使用者拍板）；本 epic 保存批次原始單價與數量即可支撐，不另存彙總成本。
