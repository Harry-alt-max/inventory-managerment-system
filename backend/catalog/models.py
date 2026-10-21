"""商品、批次、倉庫與庫存位置的資料模型（AD-8、AD-9、AD-10、AD-20）。

重點：

- **業務編號與內部主鍵分離**（AD-8）：``item_code``／``po_number`` 是顯示用編號，
  由資料庫 sequence 配置、建立後不可修改；內部主鍵仍為整數 ``id``。
- **數值型別**（AD-9）：數量為整數；金額為 ``Decimal(12,2)``；捨入一律
  ``ROUND_HALF_UP``。
- **業務日期**（AD-10）：``received_at`` 存為 ``date``，不從 timestamp 推導。
- **唯一性落在資料庫**（AD-20）：商品編號、批次流水號、倉庫編碼、
  同倉庫內的位置代碼皆以 UNIQUE constraint 落實。
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from .codes import allocate_item_code, allocate_po_number

#: 金額的最小單位（0.01 元）
MONEY_QUANTUM = Decimal("0.01")


def compute_total(unit_price: Decimal, quantity: int) -> Decimal:
    """批次總價 = 單價 × 數量，四捨五入到小數兩位（AD-9）。"""
    return (Decimal(unit_price) * Decimal(quantity)).quantize(
        MONEY_QUANTUM, rounding=ROUND_HALF_UP
    )


class Item(models.Model):
    """商品主檔（FR-4）。

    庫存數量、批次與採購單價**不由建檔填寫**（FR-4），一律由採購批次與入庫
    帶入，避免同一資料有兩個來源。
    """

    #: 商品編號（``INV-`` + 6 碼，系統配置、不可修改）
    item_code = models.CharField(
        "商品編號",
        max_length=10,
        unique=True,
        editable=False,
        default=allocate_item_code,
    )
    #: 商品名稱（必填）
    name = models.CharField("商品名稱", max_length=200)
    #: 供應商名稱（必填）
    supplier_name = models.CharField("供應商", max_length=200)
    #: 建議售價
    suggested_price = models.DecimalField(
        "建議售價", max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    #: 預計毛利
    expected_margin = models.DecimalField(
        "預計毛利", max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        db_table = "catalog_item"
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["id"]
        indexes = [models.Index(fields=["name"], name="catalog_item_name_idx")]

    def __str__(self) -> str:  # pragma: no cover - 顯示用
        return f"{self.item_code} {self.name}"


class Batch(models.Model):
    """採購批次（FR-9）。

    總價由單價 × 數量自動計算，不另外輸入；批次的單價與數量一經建立即為
    原始成本資料（AD-11），不可被彙總值取代。
    """

    #: 所屬商品
    item = models.ForeignKey(
        Item, verbose_name="商品", on_delete=models.PROTECT, related_name="batches"
    )
    #: 採購批次流水號（``PO-YYYYMMDD-NNN``，系統配置、不可修改）
    po_number = models.CharField(
        "採購批次流水號",
        max_length=16,
        unique=True,
        editable=False,
        default=allocate_po_number,
    )
    #: 供應商名稱
    supplier_name = models.CharField("供應商", max_length=200)
    #: 單價
    unit_price = models.DecimalField("單價", max_digits=12, decimal_places=2)
    #: 數量（整數）
    quantity = models.PositiveIntegerField("數量")
    #: 總價（單價 × 數量，自動計算）
    total = models.DecimalField(
        "總價", max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    #: 到貨日期（業務日期，AD-10）
    received_at = models.DateField("到貨日期")
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        db_table = "catalog_batch"
        verbose_name = "採購批次"
        verbose_name_plural = "採購批次"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["item", "received_at"], name="catalog_batch_item_date_idx")
        ]

    def save(self, *args, **kwargs):
        """總價一律由單價與數量重算，不接受外部傳入的總價。"""
        self.total = compute_total(self.unit_price, self.quantity)
        super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - 顯示用
        return f"{self.po_number} {self.item.item_code}"


class Warehouse(models.Model):
    """倉庫（FR-10）：公司內唯一的倉庫編碼。"""

    #: 倉庫編碼（唯一）
    code = models.CharField("倉庫編碼", max_length=32, unique=True)
    #: 倉庫名稱
    name = models.CharField("倉庫名稱", max_length=200)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        db_table = "catalog_warehouse"
        verbose_name = "倉庫"
        verbose_name_plural = "倉庫"
        ordering = ["code"]

    def __str__(self) -> str:  # pragma: no cover - 顯示用
        return f"{self.code} {self.name}"


class Location(models.Model):
    """庫存位置（FR-10）：位置代碼在**同一倉庫內**唯一。"""

    #: 所屬倉庫
    warehouse = models.ForeignKey(
        Warehouse, verbose_name="倉庫", on_delete=models.CASCADE, related_name="locations"
    )
    #: 位置代碼（同倉唯一）
    code = models.CharField("位置代碼", max_length=32)
    #: 位置名稱
    name = models.CharField("位置名稱", max_length=200)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        db_table = "catalog_location"
        verbose_name = "庫存位置"
        verbose_name_plural = "庫存位置"
        ordering = ["warehouse_id", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"], name="catalog_location_warehouse_code_uniq"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - 顯示用
        return f"{self.warehouse.code}/{self.code}"
