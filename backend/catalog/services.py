"""catalog 的 use case（AD-3）。

view 不得直接操作 model：所有寫入都集中在這裡的 use case 函式，並以
``transaction.atomic()`` 包住；view 只負責 HTTP 契約（AD-7）與錯誤包絡（AD-17）。

其他約定：

- **actor 為顯式參數**（AD-32）：呼叫端傳入帳號代號字串，本模組不使用
  thread-local，也不從 request 推導。
- **日誌**（AD-18）：每個 use case 都記錄 use case 名稱與 actor。
- **唯一性**（AD-20）：以資料庫 UNIQUE constraint 為唯一防線；違反時轉為
  ``resource.duplicate``（409）並在 ``field_errors`` 指回欄位。
"""
from __future__ import annotations

import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Case, IntegerField, When

from core.exceptions import DuplicateValue, ResourceNotFound, ValidationFailed

from .models import Batch, Item, Location, Warehouse

logger = logging.getLogger(__name__)

#: 金額最小單位（0.01 元）
MONEY_QUANTUM = Decimal("0.01")


# ---------------------------------------------------------------------------
# 輸入解析（所有驗證都在 use case 層，view 不做業務驗證）
# ---------------------------------------------------------------------------


def _parse_text(
    value: Any,
    field: str,
    field_errors: dict[str, list[str]],
    *,
    max_length: int,
    required: bool = True,
) -> str:
    """解析必填文字欄位；空白視為缺值（FR-4：缺項時指出缺哪一欄）。"""
    text = "" if value is None else str(value).strip()
    if not text:
        if required:
            field_errors[field] = ["This field is required."]
        return ""
    if len(text) > max_length:
        field_errors[field] = [f"Must be at most {max_length} characters."]
        return ""
    return text


def _parse_money(
    value: Any,
    field: str,
    field_errors: dict[str, list[str]],
    *,
    required: bool = True,
    allow_negative: bool = False,
) -> Decimal | None:
    """解析金額（``Decimal(12,2)``；捨入 ROUND_HALF_UP，AD-9）。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            field_errors[field] = ["This field is required."]
        return None
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ArithmeticError, ValueError):
        field_errors[field] = ["Must be a valid decimal number."]
        return None
    if not amount.is_finite():
        field_errors[field] = ["Must be a valid decimal number."]
        return None
    amount = amount.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    if not allow_negative and amount < 0:
        field_errors[field] = ["Must be zero or greater."]
        return None
    return amount


def _parse_int(
    value: Any,
    field: str,
    field_errors: dict[str, list[str]],
    *,
    required: bool = True,
    minimum: int | None = None,
) -> int | None:
    """解析整數欄位（數量為整數，AD-9）。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            field_errors[field] = ["This field is required."]
        return None
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        field_errors[field] = ["Must be an integer."]
        return None
    if minimum is not None and number < minimum:
        field_errors[field] = [f"Must be {minimum} or greater."]
        return None
    return number


def _parse_date(
    value: Any, field: str, field_errors: dict[str, list[str]]
) -> date | None:
    """解析業務日期（``date``，AD-10）。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        field_errors[field] = ["This field is required."]
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        field_errors[field] = ["Must be a date in YYYY-MM-DD format."]
        return None


def _raise_if_invalid(field_errors: dict[str, list[str]]) -> None:
    if field_errors:
        raise ValidationFailed(field_errors=field_errors)


# ---------------------------------------------------------------------------
# use case：商品（FR-4、FR-5）
# ---------------------------------------------------------------------------


@transaction.atomic
def create_item(
    *,
    actor: str,
    name: Any,
    supplier_name: Any,
    suggested_price: Any = None,
    expected_margin: Any = None,
) -> Item:
    """建立商品主檔（FR-4）。

    商品編號由資料庫 sequence 配置（``INV-`` + 6 碼），呼叫端不得指定。
    缺少名稱或供應商時拒絕儲存並在 ``field_errors`` 指出缺哪一欄。
    """
    field_errors: dict[str, list[str]] = {}
    item_name = _parse_text(name, "name", field_errors, max_length=200)
    supplier = _parse_text(supplier_name, "supplier_name", field_errors, max_length=200)
    price = _parse_money(
        suggested_price,
        "suggested_price",
        field_errors,
        required=False,
        allow_negative=False,
    )
    margin = _parse_money(
        expected_margin,
        "expected_margin",
        field_errors,
        required=False,
        allow_negative=True,
    )
    _raise_if_invalid(field_errors)

    try:
        with transaction.atomic():
            item = Item.objects.create(
                name=item_name,
                supplier_name=supplier,
                suggested_price=price if price is not None else Decimal("0.00"),
                expected_margin=margin if margin is not None else Decimal("0.00"),
            )
    except IntegrityError as exc:  # pragma: no cover - item_code 由 sequence 配置
        logger.info("use_case=create_item actor=%s result=conflict", actor)
        raise DuplicateValue(
            "Item code already exists.",
            field_errors={"item_code": ["This item code already exists."]},
        ) from exc

    logger.info(
        "use_case=create_item actor=%s item_code=%s result=success",
        actor,
        item.item_code,
    )
    return item


def list_items(*, query: str | None = None) -> list[Item]:
    """查詢商品主檔（FR-5）。

    ``query`` 為名稱的部分關鍵字；精確相同名稱優先於部分符合（FR-5）。
    """
    queryset = Item.objects.all()
    keyword = (query or "").strip()
    if keyword:
        queryset = queryset.filter(name__icontains=keyword)
        queryset = queryset.annotate(
            exact_match=Case(
                When(name__iexact=keyword, then=0), default=1, output_field=IntegerField()
            )
        ).order_by("exact_match", "id")
    else:
        queryset = queryset.order_by("id")
    return list(queryset)


def get_item(*, item_code: str) -> Item:
    """取得商品；不存在時回 404 ``resource.not_found``。"""
    item = Item.objects.filter(item_code=item_code).first()
    if item is None:
        raise ResourceNotFound(f"Item {item_code} was not found.")
    return item


def list_batches_of_item(*, item: Item) -> list[Batch]:
    """列出某商品的採購批次（隨商品明細一起回傳）。"""
    return list(item.batches.all())


# ---------------------------------------------------------------------------
# use case：採購批次（FR-9）
# ---------------------------------------------------------------------------


@transaction.atomic
def create_batch(
    *,
    actor: str,
    item_code: Any,
    po_number: Any = None,
    supplier_name: Any,
    unit_price: Any,
    quantity: Any,
    received_at: Any,
) -> Batch:
    """建立採購批次（FR-9）。

    - 單價或數量任一缺失即拒絕儲存；
    - 總價由單價 × 數量自動計算（不接受外部傳入）；
    - 批次流水號預設由資料庫 sequence 配置；亦可帶入既有的供應商採購單號
      （此時仍以資料庫 UNIQUE constraint 為唯一防線，重複回 409）。
    """
    field_errors: dict[str, list[str]] = {}
    code = _parse_text(item_code, "item_code", field_errors, max_length=10)
    supplier = _parse_text(supplier_name, "supplier_name", field_errors, max_length=200)
    price = _parse_money(unit_price, "unit_price", field_errors)
    count = _parse_int(quantity, "quantity", field_errors, minimum=1)
    received = _parse_date(received_at, "received_at", field_errors)

    explicit_po_number: str | None = None
    if po_number is not None and str(po_number).strip():
        explicit_po_number = _parse_text(
            po_number, "po_number", field_errors, max_length=16
        )

    _raise_if_invalid(field_errors)

    item = Item.objects.filter(item_code=code).first()
    if item is None:
        raise ResourceNotFound(f"Item {code} was not found.")

    if explicit_po_number is not None:
        if Batch.objects.filter(po_number=explicit_po_number).exists():
            logger.info(
                "use_case=create_batch actor=%s result=conflict po_number=%s",
                actor,
                explicit_po_number,
            )
            raise DuplicateValue(
                "Purchase order number already exists.",
                field_errors={
                    "po_number": ["A batch with this purchase order number already exists."]
                },
            )

    try:
        with transaction.atomic():
            batch = Batch.objects.create(
                item=item,
                supplier_name=supplier,
                unit_price=price,
                quantity=count,
                received_at=received,
                **({"po_number": explicit_po_number} if explicit_po_number else {}),
            )
    except IntegrityError as exc:
        logger.info("use_case=create_batch actor=%s result=conflict", actor)
        raise DuplicateValue(
            "Purchase order number already exists.",
            field_errors={
                "po_number": ["A batch with this purchase order number already exists."]
            },
        ) from exc

    logger.info(
        "use_case=create_batch actor=%s po_number=%s result=success",
        actor,
        batch.po_number,
    )
    return batch


def list_batches(*, item_code: str | None = None) -> list[Batch]:
    """列出採購批次；可依商品編號篩選。"""
    queryset = Batch.objects.select_related("item").all()
    keyword = (item_code or "").strip()
    if keyword:
        queryset = queryset.filter(item__item_code=keyword)
    return list(queryset.order_by("id"))


# ---------------------------------------------------------------------------
# use case：倉庫與庫存位置（FR-10）
# ---------------------------------------------------------------------------


@transaction.atomic
def create_warehouse(*, actor: str, code: Any, name: Any) -> Warehouse:
    """建立倉庫（FR-10）；倉庫編碼在公司內唯一。"""
    field_errors: dict[str, list[str]] = {}
    warehouse_code = _parse_text(code, "code", field_errors, max_length=32)
    warehouse_name = _parse_text(name, "name", field_errors, max_length=200)
    _raise_if_invalid(field_errors)

    try:
        with transaction.atomic():
            warehouse = Warehouse.objects.create(code=warehouse_code, name=warehouse_name)
    except IntegrityError as exc:
        logger.info("use_case=create_warehouse actor=%s result=conflict", actor)
        raise DuplicateValue(
            "Warehouse code already exists.",
            field_errors={"code": ["A warehouse with this code already exists."]},
        ) from exc

    logger.info(
        "use_case=create_warehouse actor=%s code=%s result=success", actor, warehouse.code
    )
    return warehouse


def list_warehouses() -> list[Warehouse]:
    """列出所有倉庫。"""
    return list(Warehouse.objects.all())


def get_warehouse(*, code: str) -> Warehouse:
    """取得倉庫；不存在時回 404 ``resource.not_found``。"""
    warehouse = Warehouse.objects.filter(code=code).first()
    if warehouse is None:
        raise ResourceNotFound(f"Warehouse {code} was not found.")
    return warehouse


@transaction.atomic
def create_location(*, actor: str, warehouse_code: Any, code: Any, name: Any) -> Location:
    """建立庫存位置（FR-10）；位置代碼在同一倉庫內唯一。"""
    field_errors: dict[str, list[str]] = {}
    warehouse_ref = _parse_text(warehouse_code, "warehouse_code", field_errors, max_length=32)
    location_code = _parse_text(code, "code", field_errors, max_length=32)
    location_name = _parse_text(name, "name", field_errors, max_length=200)
    _raise_if_invalid(field_errors)

    warehouse = Warehouse.objects.filter(code=warehouse_ref).first()
    if warehouse is None:
        raise ResourceNotFound(f"Warehouse {warehouse_ref} was not found.")

    try:
        with transaction.atomic():
            location = Location.objects.create(
                warehouse=warehouse, code=location_code, name=location_name
            )
    except IntegrityError as exc:
        logger.info("use_case=create_location actor=%s result=conflict", actor)
        raise DuplicateValue(
            "Location code already exists in this warehouse.",
            field_errors={
                "code": ["A location with this code already exists in this warehouse."]
            },
        ) from exc

    logger.info(
        "use_case=create_location actor=%s warehouse=%s code=%s result=success",
        actor,
        warehouse.code,
        location.code,
    )
    return location


def list_locations(*, warehouse_code: str) -> list[Location]:
    """列出某倉庫的所有庫存位置。"""
    warehouse = get_warehouse(code=warehouse_code)
    return list(warehouse.locations.all())
