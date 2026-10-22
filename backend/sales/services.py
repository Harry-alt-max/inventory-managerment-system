"""銷貨 use case（AD-3、AD-26、AD-28、AD-31）。

流程：

1. ``quote``        報價試算（不寫入）：折後金額、FIFO 成本與毛利
2. ``create_order`` 建立草稿銷貨單（草稿不動庫存）
3. ``submit_order`` 送出：同一交易內重算 FIFO 成本、扣減庫存、寫入庫存異動與批次消耗
4. ``reverse_order`` 沖銷：反向加回庫存並留下沖銷紀錄（原單不刪除）

毛利定義（AD-18）：``折後金額 − 成本``；成本為 FIFO 依序消耗的批次單價 × 數量。
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from django.db import connection, transaction
from django.utils import timezone

from catalog.models import Item, Location
from core.exceptions import (
    Conflict,
    InsufficientStock,
    ResourceNotFound,
    ValidationFailed,
)
from stock.models import StockLevel, StockMovement
from stock.services import available_by_batch

from .models import BatchConsumption, SalesOrder, SalesOrderLine

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def _money(value) -> Decimal:
    """金額一律小數兩位、ROUND_HALF_UP（AD-9）。"""
    return Decimal(value or 0).quantize(CENT, rounding=ROUND_HALF_UP)


def _rate(value) -> Decimal:
    """折扣率（百分比）檢查。"""
    try:
        rate = Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
    except Exception as exc:  # noqa: BLE001 - 非數字輸入
        raise ValidationFailed(field_errors={"discount_rate": ["折扣率必須是數字。"]}) from exc
    if rate < 0 or rate > 100:
        raise ValidationFailed(field_errors={"discount_rate": ["折扣率必須在 0～100 之間。"]})
    return rate


def allocate_order_no() -> str:
    """配置銷貨單號 ``SO-YYYYMMDD-NNN``（AD-8）。"""
    business_date = timezone.localdate()
    with connection.cursor() as cursor:
        cursor.execute("CREATE SEQUENCE IF NOT EXISTS sales_order_no_seq")
        cursor.execute("SELECT nextval('sales_order_no_seq')")
        value = int(cursor.fetchone()[0])
    return f"SO-{business_date:%Y%m%d}-{value:03d}"


def _fifo_cost(item: Item, location: Location, quantity: int) -> tuple[Decimal, list[dict]]:
    """依 FIFO 計算某商品某位置的成本，並回傳批次消耗明細（AD-31）。

    FIFO 的排序鍵是**該批次的入庫時間**（由異動紀錄推得），不是批次建立時間。
    """
    remaining = quantity
    cost = ZERO
    consumptions: list[dict] = []
    for row in available_by_batch(item, location):
        if remaining <= 0:
            break
        take = min(remaining, row["remaining"])
        line_cost = _money(Decimal(row["unit_price"]) * take)
        cost += line_cost
        consumptions.append(
            {
                "batch": row["batch"],
                "quantity": take,
                "unit_price": row["unit_price"],
                "cost": line_cost,
            }
        )
        remaining -= take
    if remaining > 0:
        available = sum(row["remaining"] for row in available_by_batch(item, location))
        raise InsufficientStock(
            f"可用數量不足：需要 {quantity}，目前可用 {available}。",
            field_errors={
                "quantity": [f"可用數量不足：需要 {quantity}，目前可用 {available}。"]
            },
        )
    return _money(cost), consumptions


def quote(lines: list[dict], discount_rate=0) -> dict:
    """報價試算（不寫入任何資料，AD-26）。

    回傳每行的售價小計、FIFO 成本，以及整單的原價合計、折扣、折後金額與毛利。
    """
    rate = _rate(discount_rate)
    quoted: list[dict] = []
    total_amount = ZERO
    total_cost = ZERO

    for index, raw in enumerate(lines or []):
        raw = raw or {}
        item_code = str(raw.get("item_code") or "").strip()
        location_code = str(raw.get("location_code") or "").strip()
        if not item_code:
            raise ValidationFailed(field_errors={"item_code": [f"第 {index + 1} 列缺少商品編號。"]})
        if not location_code:
            raise ValidationFailed(
                field_errors={"location_code": [f"第 {index + 1} 列缺少庫存位置。"]}
            )
        try:
            quantity = int(raw.get("quantity") or 0)
        except (TypeError, ValueError) as exc:
            raise ValidationFailed(
                field_errors={"quantity": [f"第 {index + 1} 列的數量不正確。"]}
            ) from exc
        if quantity <= 0:
            raise ValidationFailed(
                field_errors={"quantity": [f"第 {index + 1} 列的數量必須是正整數。"]}
            )

        item = Item.objects.filter(item_code=item_code).first()
        if item is None:
            raise ResourceNotFound(f"找不到商品 {item_code}。")
        location = Location.objects.filter(code=location_code).first()
        if location is None:
            raise ResourceNotFound(f"找不到庫存位置 {location_code}。")

        unit_price = _money(
            raw.get("unit_price") if raw.get("unit_price") not in (None, "") else item.suggested_price
        )
        subtotal = _money(unit_price * quantity)
        cost, consumptions = _fifo_cost(item, location, quantity)

        quoted.append(
            {
                "item_code": item.item_code,
                "item_name": item.name,
                "location_code": location.code,
                "quantity": quantity,
                "unit_price": str(unit_price),
                "subtotal": str(subtotal),
                "cost": str(cost),
                "consumptions": [
                    {
                        "po_number": item_batch["batch"].po_number,
                        "quantity": item_batch["quantity"],
                        "unit_price": str(item_batch["unit_price"]),
                        "cost": str(item_batch["cost"]),
                    }
                    for item_batch in consumptions
                ],
            }
        )
        total_amount += subtotal
        total_cost += cost

    discount_amount = _money(total_amount * rate / Decimal(100))
    total_paid = _money(total_amount - discount_amount)
    total_margin = _money(total_paid - total_cost)

    return {
        "lines": quoted,
        "total_amount": str(_money(total_amount)),
        "discount_rate": str(rate),
        "discount_amount": str(discount_amount),
        "total_paid": str(total_paid),
        "total_cost": str(_money(total_cost)),
        "total_margin": str(total_margin),
    }


@transaction.atomic
def create_order(
    *, actor: str, lines: list[dict], discount_rate=0, note: str = ""
) -> SalesOrder:
    """建立草稿銷貨單（草稿不動庫存，AD-22）。"""
    rate = _rate(discount_rate)
    if not lines:
        raise ValidationFailed(field_errors={"lines": ["銷貨單至少需要一列商品。"]})

    prepared = []
    seen: set[tuple[str, str]] = set()
    for index, raw in enumerate(lines or []):
        raw = raw or {}
        item_code = str(raw.get("item_code") or "").strip()
        location_code = str(raw.get("location_code") or "").strip()
        item = Item.objects.filter(item_code=item_code).first()
        if item is None:
            raise ResourceNotFound(f"找不到商品 {item_code}。")
        location = Location.objects.filter(code=location_code).first()
        if location is None:
            raise ResourceNotFound(f"找不到庫存位置 {location_code}。")
        key = (item_code, location_code)
        if key in seen:
            # 同一商品不得在同一張單重複列示（AD-22）
            raise ValidationFailed(
                field_errors={
                    "lines": [
                        f"第 {index + 1} 列的商品 {item_code} 在這張單重複出現（同一商品只能出現一次）。"
                    ]
                }
            )
        seen.add(key)
        try:
            quantity = int(raw.get("quantity") or 0)
        except (TypeError, ValueError) as exc:
            raise ValidationFailed(
                field_errors={"quantity": [f"第 {index + 1} 列的數量不正確。"]}
            ) from exc
        if quantity <= 0:
            raise ValidationFailed(
                field_errors={"quantity": [f"第 {index + 1} 列的數量必須是正整數。"]}
            )
        unit_price = _money(
            raw.get("unit_price")
            if raw.get("unit_price") not in (None, "")
            else item.suggested_price
        )
        prepared.append((item, location, quantity, unit_price))

    order = SalesOrder.objects.create(
        order_no=allocate_order_no(),
        status=SalesOrder.STATUS_DRAFT,
        discount_rate=rate,
        created_by=actor,
        note=note or "",
    )
    for item, location, quantity, unit_price in prepared:
        SalesOrderLine.objects.create(
            order=order,
            item=item,
            location=location,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=_money(unit_price * quantity),
        )
    return order


@transaction.atomic
def submit_order(*, actor: str, order_no: str) -> SalesOrder:
    """送出銷貨單：同一交易內扣庫存、寫異動與批次消耗（AD-28、AD-30）。"""
    order = (
        SalesOrder.objects.select_for_update()
        .filter(order_no=order_no)
        .prefetch_related("lines")
        .first()
    )
    if order is None:
        raise ResourceNotFound(f"找不到銷貨單 {order_no}。")
    if order.status != SalesOrder.STATUS_DRAFT:
        raise Conflict(f"銷貨單 {order_no} 已是「{order.get_status_display()}」，不可重複送出。")

    lines = list(order.lines.all())
    if not lines:
        raise ValidationFailed(field_errors={"lines": ["銷貨單沒有商品列。"]})

    # 1. 先鎖住涉及的庫存現況並檢查可用量
    levels: dict[tuple[int, int], StockLevel] = {}
    for line in lines:
        key = (line.item_id, line.location_id)
        if key in levels:
            continue
        level = (
            StockLevel.objects.select_for_update()
            .filter(item_id=line.item_id, location_id=line.location_id)
            .first()
        )
        if level is None:
            raise InsufficientStock(
                f"{line.item.item_code} 在 {line.location.code} 沒有庫存紀錄。",
                field_errors={"quantity": [f"{line.item.item_code} 在 {line.location.code} 沒有庫存。"]},
            )
        levels[key] = level

    for line in lines:
        level = levels[(line.item_id, line.location_id)]
        if level.quantity < line.quantity:
            raise InsufficientStock(
                f"可用數量不足：{line.item.item_code} 需要 {line.quantity}，目前可用 {level.quantity}。",
                field_errors={
                    "quantity": [
                        f"可用數量不足：{line.item.item_code} 需要 {line.quantity}，目前可用 {level.quantity}。"
                    ]
                },
            )

    # 2. 重算 FIFO 成本與消耗明細（送出時的庫存才是準）
    total_amount = ZERO
    total_cost = ZERO
    now = timezone.now()
    for line in lines:
        cost, consumptions = _fifo_cost(line.item, line.location, line.quantity)
        line.cost = cost
        line.subtotal = _money(line.unit_price * line.quantity)
        line.save(update_fields=["cost", "subtotal"])
        total_amount += line.subtotal
        total_cost += cost

        for consumption in consumptions:
            batch = consumption["batch"]
            quantity = consumption["quantity"]
            BatchConsumption.objects.create(
                line=line,
                batch=batch,
                quantity=quantity,
                unit_price=consumption["unit_price"],
                cost=consumption["cost"],
            )
            StockMovement.objects.create(
                item=line.item,
                location=line.location,
                batch=batch,
                quantity=-quantity,
                purpose=StockMovement.PURPOSE_SALE,
                actor_username=actor,
                occurred_at=now,
                note=order.order_no,
            )
            level = levels[(line.item_id, line.location_id)]
            level.quantity -= quantity
            level.save(update_fields=["quantity", "updated_at"])

    discount_amount = _money(total_amount * order.discount_rate / Decimal(100))
    total_paid = _money(total_amount - discount_amount)
    order.total_amount = _money(total_amount)
    order.total_discount = discount_amount
    order.total_paid = total_paid
    order.total_cost = _money(total_cost)
    order.total_margin = _money(total_paid - total_cost)
    order.status = SalesOrder.STATUS_SUBMITTED
    order.submitted_at = now
    order.save(
        update_fields=[
            "total_amount",
            "total_discount",
            "total_paid",
            "total_cost",
            "total_margin",
            "status",
            "submitted_at",
        ]
    )
    return order


@transaction.atomic
def reverse_order(*, actor: str, order_no: str) -> SalesOrder:
    """沖銷已送出的銷貨單：反向加回庫存並留下沖銷紀錄（原單不刪除，AD-19、AD-28）。"""
    order = (
        SalesOrder.objects.select_for_update()
        .filter(order_no=order_no)
        .prefetch_related("lines__consumptions")
        .first()
    )
    if order is None:
        raise ResourceNotFound(f"找不到銷貨單 {order_no}。")
    if order.status != SalesOrder.STATUS_SUBMITTED:
        raise Conflict(f"銷貨單 {order_no} 不是「已送出」狀態，不可沖銷。")

    now = timezone.now()
    for line in order.lines.all():
        for consumption in line.consumptions.all():
            level, _ = StockLevel.objects.select_for_update().get_or_create(
                item=line.item, location=line.location, defaults={"quantity": 0}
            )
            level.quantity += consumption.quantity
            level.save(update_fields=["quantity", "updated_at"])
            StockMovement.objects.create(
                item=line.item,
                location=line.location,
                batch=consumption.batch,
                quantity=consumption.quantity,
                purpose=StockMovement.PURPOSE_SALE_REVERSAL,
                actor_username=actor,
                occurred_at=now,
                note=order.order_no,
            )

    order.status = SalesOrder.STATUS_REVERSED
    order.save(update_fields=["status"])
    return order


def get_order(order_no: str) -> SalesOrder:
    order = (
        SalesOrder.objects.filter(order_no=order_no)
        .prefetch_related("lines__consumptions")
        .first()
    )
    if order is None:
        raise ResourceNotFound(f"找不到銷貨單 {order_no}。")
    return order


def list_orders(
    *, order_no: str = "", date_from: str = "", date_to: str = ""
) -> list[SalesOrder]:
    """銷貨紀錄查詢（毛利查核用，會計唯讀）。"""
    orders = SalesOrder.objects.prefetch_related("lines")
    order_no = (order_no or "").strip()
    if order_no:
        orders = orders.filter(order_no__icontains=order_no)
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    return list(orders.order_by("-created_at", "-id")[:200])
