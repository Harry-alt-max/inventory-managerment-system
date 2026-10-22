"""銷貨 app：銷貨單、批次消耗與毛利（AD-26、AD-28、AD-31）。

- ``SalesOrder`` 是**銷貨事實的唯一 home**（AD-28）：銷貨行、批次消耗明細與
  對應的庫存異動在**同一個交易**內寫入。
- 成本以 **FIFO** 計算（AD-11、AD-31）：依批次的入庫時間順序消耗批次。
"""
from django.db import models

from catalog.models import Batch, Item, Location


class SalesOrder(models.Model):
    """銷貨單（草稿／已送出／已沖銷）。"""

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_REVERSED = "reversed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_SUBMITTED, "已送出"),
        (STATUS_REVERSED, "已沖銷"),
    ]

    order_no = models.CharField("銷貨單號", max_length=40, unique=True)
    status = models.CharField("狀態", max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    #: 整單折扣率（百分比，0～100；AD-9 固定小數兩位）
    discount_rate = models.DecimalField("折扣率", max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField("原價合計", max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField("折扣金額", max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField("折後金額", max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField("成本合計", max_digits=12, decimal_places=2, default=0)
    total_margin = models.DecimalField("毛利", max_digits=12, decimal_places=2, default=0)
    created_by = models.CharField("建立人", max_length=150)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    submitted_at = models.DateTimeField("送出時間", null=True, blank=True)
    note = models.CharField("備註", max_length=255, blank=True, default="")

    class Meta:
        db_table = "sales_order"
        verbose_name = "銷貨單"
        verbose_name_plural = "銷貨單"
        ordering = ["-created_at", "-id"]


class SalesOrderLine(models.Model):
    """銷貨行：商品 × 位置 × 數量（AD-30：位置必填）。"""

    order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name="lines")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="sale_lines")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="sale_lines")
    quantity = models.PositiveIntegerField("數量")
    unit_price = models.DecimalField("單價", max_digits=12, decimal_places=2)
    subtotal = models.DecimalField("小計", max_digits=12, decimal_places=2, default=0)
    cost = models.DecimalField("成本", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "sales_order_line"
        verbose_name = "銷貨行"
        verbose_name_plural = "銷貨行"
        ordering = ["id"]


class BatchConsumption(models.Model):
    """批次消耗明細：這張銷貨行消耗了哪些批次的多少數量（AD-31）。"""

    line = models.ForeignKey(SalesOrderLine, on_delete=models.PROTECT, related_name="consumptions")
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, related_name="consumptions")
    quantity = models.PositiveIntegerField("數量")
    unit_price = models.DecimalField("批次單價", max_digits=12, decimal_places=2)
    cost = models.DecimalField("成本", max_digits=12, decimal_places=2)

    class Meta:
        db_table = "sales_batch_consumption"
        verbose_name = "批次消耗"
        verbose_name_plural = "批次消耗"
        ordering = ["id"]
