"""MVP 基本驗收：商品／批次／倉庫位置（catalog）與入庫（stock）。

對應 PRD：FR-4、FR-5、FR-7、FR-9、FR-10、FR-11、FR-6 與 FR-2 的權限規則。
"""
from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import Batch, Item, Location, Warehouse
from stock.models import StockLevel, StockMovement

pytestmark = pytest.mark.django_db


@pytest.fixture
def warehouse() -> Warehouse:
    return Warehouse.objects.create(code="A1", name="A 倉")


@pytest.fixture
def location(warehouse: Warehouse) -> Location:
    return Location.objects.create(warehouse=warehouse, code="A-03", name="A 區 03 架")


@pytest.fixture
def item() -> Item:
    return Item.objects.create(
        name="六角螺絲 M8x40",
        supplier_name="甲供應商",
        suggested_price="12.50",
        expected_margin="3.00",
    )


@pytest.fixture
def batch(item: Item) -> Batch:
    return Batch.objects.create(
        item=item,
        supplier_name="甲供應商",
        unit_price="12.50",
        quantity=100,
        received_at="2026-10-21",
    )


def _login(client, username: str, role: str = "warehouse") -> User:
    """建立測試帳號、指派角色群組（同步權限）並登入。"""
    from django.contrib.auth.models import Group, Permission

    from core.permissions import ROLE_GROUP_NAMES, ROLE_PERMISSIONS

    user = User.objects.create_user(username=username, password="pw-for-test-1234")
    group, _ = Group.objects.get_or_create(name=ROLE_GROUP_NAMES[role])
    codenames = {codename.split(".", 1)[-1] for codename in ROLE_PERMISSIONS[role]}
    group.permissions.set(
        Permission.objects.filter(content_type__app_label="accounts", codename__in=codenames)
    )
    user.groups.set([group])
    client.force_login(user)
    return user


# ---------------------------------------------------------------------------
# catalog
# ---------------------------------------------------------------------------


def test_item_code_is_auto_allocated():
    """商品編號由資料庫 sequence 產生（AD-8），且不重複。"""
    first = Item.objects.create(name="甲", supplier_name="甲供應商")
    second = Item.objects.create(name="乙", supplier_name="甲供應商")

    assert first.item_code.startswith("INV-")
    assert first.item_code != second.item_code


def test_batch_total_is_unit_price_times_quantity(item: Item):
    """批次總價由單價 × 數量自動計算（AD-9）。"""
    batch = Batch.objects.create(
        item=item,
        supplier_name="甲供應商",
        unit_price="12.50",
        quantity=100,
        received_at="2026-10-21",
    )

    assert float(batch.total) == 1250.0


def test_po_number_is_auto_allocated_and_unique(item: Item):
    """採購批次流水號自動產生且不重複（AD-8、AD-20）。"""
    first = Batch.objects.create(
        item=item, supplier_name="甲", unit_price="1.00", quantity=1, received_at="2026-10-21"
    )
    second = Batch.objects.create(
        item=item, supplier_name="甲", unit_price="1.00", quantity=1, received_at="2026-10-21"
    )

    assert first.po_number.startswith("PO-")
    assert first.po_number != second.po_number


def test_duplicate_location_code_in_same_warehouse_is_refused(warehouse: Warehouse):
    """同一倉庫內位置代碼不得重複（AD-20）。"""
    Location.objects.create(warehouse=warehouse, code="A-03", name="A")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Location.objects.create(warehouse=warehouse, code="A-03", name="A again")


# ---------------------------------------------------------------------------
# stock
# ---------------------------------------------------------------------------


def test_inbound_updates_stock_level_and_creates_movement(
    client, item: Item, batch: Batch, location: Location
):
    """入庫後庫存現況增加，並留下一筆含操作人員與批次的異動（AD-11、AD-29）。"""
    user = _login(client, "wh")

    response = client.post(
        "/api/v1/stock/inbound",
        {
            "item_code": item.item_code,
            "location_code": location.code,
            "batch_po_number": batch.po_number,
            "quantity": 50,
        },
        content_type="application/json",
    )

    assert response.status_code == 201, response.content
    level = StockLevel.objects.get(item=item, location=location)
    assert level.quantity == 50
    movement = StockMovement.objects.get()
    assert movement.quantity == 50
    assert movement.purpose == StockMovement.PURPOSE_INBOUND
    assert movement.actor_username == user.get_username()
    assert movement.batch_id == batch.id


def test_inbound_rejects_missing_fields(client, item: Item, batch: Batch, location: Location):
    """缺數量／位置／批次時拒絕並指出缺哪一欄（AD-7）。"""
    _login(client, "wh2")

    response = client.post(
        "/api/v1/stock/inbound",
        {"item_code": item.item_code, "quantity": 0},
        content_type="application/json",
    )

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"code", "detail", "field_errors"}
    assert "location_code" in body["field_errors"]


def test_batch_must_belong_to_item(client, item: Item, location: Location):
    """批次不屬於該商品時拒絕（避免成本掛錯商品）。"""
    other = Item.objects.create(name="其他", supplier_name="甲")
    other_batch = Batch.objects.create(
        item=other, supplier_name="甲", unit_price="1.00", quantity=1, received_at="2026-10-21"
    )
    _login(client, "wh3")

    response = client.post(
        "/api/v1/stock/inbound",
        {
            "item_code": item.item_code,
            "location_code": location.code,
            "batch_po_number": other_batch.po_number,
            "quantity": 5,
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "batch_po_number" in response.json()["field_errors"]


def test_movement_is_append_only(item: Item, batch: Batch, location: Location):
    """異動紀錄不可修改或刪除（AD-12）。"""
    movement = StockMovement.objects.create(
        item=item,
        location=location,
        batch=batch,
        quantity=1,
        purpose=StockMovement.PURPOSE_INBOUND,
        actor_username="wh",
        occurred_at="2026-10-21T00:00:00Z",
    )

    movement.quantity = 999
    with pytest.raises(ValueError):
        movement.save()
    with pytest.raises(ValueError):
        movement.delete()


def test_accounting_role_cannot_inbound(client, item: Item, batch: Batch, location: Location):
    """會計為唯讀角色，入庫被拒（AD-5）。"""
    _login(client, "acct", role="accounting")

    response = client.post(
        "/api/v1/stock/inbound",
        {
            "item_code": item.item_code,
            "location_code": location.code,
            "batch_po_number": batch.po_number,
            "quantity": 1,
        },
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.forbidden"


def test_stock_list_matches_location_totals(client, item: Item, location: Location):
    """庫存查詢回應的數量與各位置加總一致（AD-29）。"""
    _login(client, "wh4")
    StockLevel.objects.create(item=item, location=location, quantity=7)

    response = client.get("/api/v1/stock")

    assert response.status_code == 200
    rows = response.json()["stock"]
    assert rows[0]["quantity"] == 7
    assert rows[0]["item_code"] == item.item_code
