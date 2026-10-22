"""庫存現況與庫存異動紀錄（AD-29、AD-12）。

- ``StockLevel``（商品 × 位置）是庫存數量的**唯一真相**（AD-29），
  由入庫等 use case 在同一交易內更新。
- ``StockMovement`` 是**僅追加**的異動明細（AD-12）：每筆記錄商品、位置、
  批次、數量正負號、用途與操作人員。
"""
from django.db import models

from catalog.models import Batch, Item, Location


class StockLevel(models.Model):
    """庫存現況：商品 × 位置 × 數量。"""

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="stock_levels")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="stock_levels")
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock_stock_level"
        verbose_name = "庫存現況"
        verbose_name_plural = "庫存現況"
        constraints = [
            models.UniqueConstraint(
                fields=["item", "location"], name="uniq_stock_level_item_location"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0), name="stock_level_quantity_non_negative"
            ),
        ]


class StockMovement(models.Model):
    """庫存異動紀錄（僅追加，不可修改或刪除）。"""

    PURPOSE_INBOUND = "inbound"
    PURPOSE_ISSUE = "issue"
    PURPOSE_TRANSFER_OUT = "transfer_out"
    PURPOSE_TRANSFER_IN = "transfer_in"
    PURPOSE_SALE = "sale"
    PURPOSE_SALE_REVERSAL = "sale_reversal"
    PURPOSE_CHOICES = [
        (PURPOSE_INBOUND, "入庫"),
        (PURPOSE_ISSUE, "領用"),
        (PURPOSE_TRANSFER_OUT, "移轉出"),
        (PURPOSE_TRANSFER_IN, "移轉入"),
        (PURPOSE_SALE, "銷貨出庫"),
        (PURPOSE_SALE_REVERSAL, "銷貨沖銷回庫"),
    ]

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="movements")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="movements")
    batch = models.ForeignKey(
        Batch, on_delete=models.PROTECT, null=True, blank=True, related_name="movements"
    )
    #: 正數為入庫、負數為出庫
    quantity = models.IntegerField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    #: 操作人員代號快照（AD-32：帳號改名或停用不影響既有紀錄）
    actor_username = models.CharField(max_length=150)
    occurred_at = models.DateTimeField()
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "stock_stock_movement"
        verbose_name = "庫存異動"
        verbose_name_plural = "庫存異動"
        ordering = ["-occurred_at", "-id"]

    def save(self, *args, **kwargs):
        """僅追加：已存在的紀錄不可修改（AD-12）。"""
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("庫存異動紀錄不可修改（僅追加）。")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """僅追加：不可刪除（AD-12）。"""
        raise ValueError("庫存異動紀錄不可刪除（僅追加）。")
