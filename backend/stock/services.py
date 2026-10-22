"""庫存 use case（AD-3：寫入只經過 service，view 不直接操作 model）。"""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from catalog.models import Batch, Item, Location
from core.email import send_notification
from core.exceptions import Conflict, InsufficientStock, ResourceNotFound, ValidationFailed

from .models import StockLevel, StockMovement


def _require(value, field: str, label: str):
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationFailed(field_errors={field: [f"{label}為必填。"]})
    return value


def get_item(item_code: str) -> Item:
    item = Item.objects.filter(item_code=item_code).first()
    if item is None:
        raise ResourceNotFound(f"找不到商品 {item_code}。")
    return item


def get_location(location_code: str) -> Location:
    location = Location.objects.filter(code=location_code).first()
    if location is None:
        raise ResourceNotFound(f"找不到庫存位置 {location_code}。")
    return location


def get_batch(po_number: str) -> Batch:
    batch = Batch.objects.filter(po_number=po_number).first()
    if batch is None:
        raise ResourceNotFound(f"找不到採購批次 {po_number}。")
    return batch


@transaction.atomic
def receive_stock(
    *,
    actor: str,
    item_code: str,
    location_code: str,
    batch_po_number: str,
    quantity: int,
    note: str = "",
) -> StockMovement:
    """入庫：更新庫存現況並留下一筆異動（AD-11、AD-29）。

    - 單價取自批次，不得另行輸入（AD-11）
    - 庫存數量不得為負（AD-4）
    - 同一交易內更新現況與寫入異動（AD-3）
    """
    _require(item_code, "item_code", "商品編號")
    _require(location_code, "location_code", "庫存位置")
    _require(batch_po_number, "batch_po_number", "採購批次")
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValidationFailed(field_errors={"quantity": ["入庫數量必須是正整數。"]})

    item = get_item(item_code)
    location = get_location(location_code)
    batch = get_batch(batch_po_number)
    if batch.item_id != item.id:
        raise ValidationFailed(
            field_errors={"batch_po_number": ["該採購批次不屬於此商品。"]}
        )

    level, _created = StockLevel.objects.select_for_update().get_or_create(
        item=item, location=location, defaults={"quantity": 0}
    )
    level.quantity += quantity
    level.save(update_fields=["quantity", "updated_at"])

    movement = StockMovement.objects.create(
        item=item,
        location=location,
        batch=batch,
        quantity=quantity,
        purpose=StockMovement.PURPOSE_INBOUND,
        actor_username=actor,
        occurred_at=timezone.now(),
        note=note or "",
    )

    # 入庫通知信：交易提交後才寄，避免交易回滾卻已寄信（transaction.on_commit）
    transaction.on_commit(
        lambda: _notify_inbound(
            actor=actor,
            item_name=item.name,
            item_code=item.item_code,
            location_code=location.code,
            batch_po_number=batch.po_number,
            quantity=quantity,
        )
    )
    return movement


def _notify_inbound(
    *,
    actor: str,
    item_name: str,
    item_code: str,
    location_code: str,
    batch_po_number: str,
    quantity: int,
) -> None:
    """寄出入庫通知信；寄信失敗不影響入庫結果（見 ``core.email``）。"""
    body = (
        f"商品：{item_name}（{item_code}）\n"
        f"庫位：{location_code}\n"
        f"批次：{batch_po_number}\n"
        f"數量：{quantity}\n"
        f"操作人：{actor}\n"
    )
    send_notification(
        subject=f"[庫存管理系統] 入庫通知：{item_name} × {quantity}",
        body=body,
    )


def list_stock(query: str = "") -> list[StockLevel]:
    """庫存現況清單：商品名稱部分符合過濾，依商品編號排序。"""
    levels = StockLevel.objects.select_related("item", "location", "location__warehouse")
    query = (query or "").strip()
    if query:
        levels = levels.filter(item__name__icontains=query)
    return list(levels.order_by("item__item_code", "location__code"))


def list_movements(
    *,
    item_code: str = "",
    purpose: str = "",
    limit: int = 100,
) -> list[StockMovement]:
    """庫存異動紀錄查詢（依商品、用途過濾）。"""
    movements = StockMovement.objects.select_related("item", "location", "batch")
    item_code = (item_code or "").strip()
    if item_code:
        movements = movements.filter(item__item_code=item_code)
    purpose = (purpose or "").strip()
    if purpose:
        movements = movements.filter(purpose=purpose)
    return list(movements.order_by("-occurred_at", "-id")[:limit])


def available_by_batch(item: Item, location: Location) -> list[dict]:
    """某商品在某位置的**批次剩餘量**，依入庫時間排序（FIFO，AD-31）。

    剩餘量由異動紀錄推算（入庫為正、出庫為負），故排序鍵是該批次的
    第一次入庫時間，而不是批次建立時間。
    """
    from django.db.models import Min, Sum

    inbound = (
        StockMovement.objects.filter(item=item, location=location)
        .exclude(batch__isnull=True)
        .values("batch_id")
        .annotate(first_in=Min("occurred_at"))
    )
    net = (
        StockMovement.objects.filter(item=item, location=location)
        .exclude(batch__isnull=True)
        .values("batch_id")
        .annotate(net=Sum("quantity"))
    )
    first_in_map = {row["batch_id"]: row["first_in"] for row in inbound}
    net_map = {row["batch_id"]: row["net"] for row in net}
    if not net_map:
        return []

    batches = {
        batch.id: batch
        for batch in Batch.objects.filter(id__in=list(net_map.keys())).select_related("item")
    }
    rows: list[dict] = []
    for batch_id, net in net_map.items():
        batch = batches.get(batch_id)
        if batch is None or net <= 0:
            continue
        rows.append(
            {
                "batch": batch,
                "remaining": net,
                "unit_price": batch.unit_price,
                "first_in": first_in_map.get(batch_id),
            }
        )
    rows.sort(key=lambda row: (row["first_in"] or timezone.now(), row["batch"].po_number))
    return rows


def check_available(item: Item, location: Location, quantity: int) -> None:
    """確認可用量足夠；不足時拋出 ``stock.insufficient``（AD-4）。"""
    level = StockLevel.objects.filter(item=item, location=location).first()
    available = level.quantity if level else 0
    if available < quantity:
        raise InsufficientStock(
            f"可用數量不足：需要 {quantity}，目前可用 {available}。",
            field_errors={"quantity": [f"可用數量不足：需要 {quantity}，目前可用 {available}。"]},
        )
