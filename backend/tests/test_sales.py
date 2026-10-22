"""銷貨與毛利測試（PRD FR-16～FR-19、FR-2）。

涵蓋：草稿不動庫存、送出扣庫存並留下異動與批次消耗、FIFO 成本、毛利計算、
超量拒絕、重複商品拒絕、沖銷回加庫存、會計唯讀可查不可寫。
"""
from __future__ import annotations

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command

from accounts.models import User
from catalog.models import Batch, Item, Location, Warehouse
from core.permissions import ROLE_GROUP_NAMES, ROLE_PERMISSIONS
from stock.models import StockLevel, StockMovement

pytestmark = pytest.mark.django_db


def _login(client, username: str, role: str) -> User:
    """建立測試帳號、指派角色群組（同步權限）並登入。"""
    user = User.objects.create_user(username=username, password="pw-for-test-1234")
    group, _ = Group.objects.get_or_create(name=ROLE_GROUP_NAMES[role])
    codenames = {codename.split(".", 1)[-1] for codename in ROLE_PERMISSIONS[role]}
    group.permissions.set(
        Permission.objects.filter(content_type__app_label="accounts", codename__in=codenames)
    )
    user.groups.set([group])
    client.force_login(user)
    return user


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
        suggested_price="20.00",
        expected_margin="5.00",
    )


def _receive(item: Item, location: Location, *, price: str, quantity: int, po: str) -> Batch:
    """直接建立批次並入庫（測試用，略過 API）。"""
    from django.utils import timezone

    from stock.services import receive_stock

    batch = Batch.objects.create(
        item=item,
        supplier_name="甲供應商",
        unit_price=price,
        quantity=quantity,
        received_at=timezone.localdate(),
    )
    receive_stock(
        actor="tester",
        item_code=item.item_code,
        location_code=location.code,
        batch_po_number=batch.po_number,
        quantity=quantity,
    )
    return batch


def test_draft_does_not_touch_stock(client, item: Item, location: Location):
    """草稿銷貨單不動庫存（AD-22）。"""
    _login(client, "sales1", "sales")
    _receive(item, location, price="10.00", quantity=100, po="A")

    response = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 5}
            ],
            "discount_rate": 0,
        },
        content_type="application/json",
    )

    assert response.status_code == 201, response.content
    assert response.json()["order"]["status"] == "draft"
    assert StockLevel.objects.get(item=item, location=location).quantity == 100


def test_submit_deducts_stock_and_records_movement(client, item: Item, location: Location):
    """送出後扣庫存、留下用途為 sale 的異動與批次消耗（AD-28、AD-30）。"""
    _login(client, "sales2", "sales")
    batch = _receive(item, location, price="10.00", quantity=100, po="B")

    created = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {
                    "item_code": item.item_code,
                    "location_code": location.code,
                    "quantity": 30,
                    "unit_price": "20.00",
                }
            ],
            "discount_rate": 0,
        },
        content_type="application/json",
    )
    order_no = created.json()["order"]["order_no"]

    submitted = client.post(f"/api/v1/sales/orders/{order_no}/submit", {}, content_type="application/json")

    assert submitted.status_code == 200, submitted.content
    order = submitted.json()["order"]
    assert order["status"] == "submitted"
    # 庫存 100 - 30 = 70
    assert StockLevel.objects.get(item=item, location=location).quantity == 70
    # 異動：sale、數量 -30、批次正確
    movement = StockMovement.objects.get(purpose=StockMovement.PURPOSE_SALE)
    assert movement.quantity == -30
    assert movement.batch_id == batch.id
    assert movement.actor_username == "sales2"
    # 批次消耗明細
    line = order["lines"][0]
    assert line["consumptions"][0]["po_number"] == batch.po_number
    assert line["consumptions"][0]["quantity"] == 30


def test_fifo_cost_uses_the_oldest_batch_first(client, item: Item, location: Location):
    """成本依 FIFO：先消耗較早入庫的批次（AD-11、AD-31）。"""
    _login(client, "sales3", "sales")
    _receive(item, location, price="10.00", quantity=60, po="C")  # 先入庫、便宜
    _receive(item, location, price="12.00", quantity=60, po="D")  # 後入庫、較貴

    quote = client.post(
        "/api/v1/sales/quote",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 80}
            ],
            "discount_rate": 0,
        },
        content_type="application/json",
    )

    assert quote.status_code == 200, quote.content
    result = quote.json()
    # 成本 = 60 × 10 + 20 × 12 = 840
    assert result["total_cost"] == "840.00"
    consumptions = result["lines"][0]["consumptions"]
    assert [c["quantity"] for c in consumptions] == [60, 20]


def test_margin_is_net_amount_minus_cost(client, item: Item, location: Location):
    """毛利 = 折後金額 − 成本（AD-18）。"""
    _login(client, "sales4", "sales")
    _receive(item, location, price="10.00", quantity=100, po="E")

    quote = client.post(
        "/api/v1/sales/quote",
        {
            "lines": [
                {
                    "item_code": item.item_code,
                    "location_code": location.code,
                    "quantity": 10,
                    "unit_price": "20.00",
                }
            ],
            "discount_rate": 10,
        },
        content_type="application/json",
    )

    result = quote.json()
    assert result["total_amount"] == "200.00"
    assert result["discount_amount"] == "20.00"
    assert result["total_paid"] == "180.00"
    assert result["total_cost"] == "100.00"
    assert result["total_margin"] == "80.00"


def test_selling_more_than_stock_is_refused(client, item: Item, location: Location):
    """超過可用量時拒絕（AD-4）。"""
    _login(client, "sales5", "sales")
    _receive(item, location, price="10.00", quantity=10, po="F")

    created = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 20}
            ]
        },
        content_type="application/json",
    )
    order_no = created.json()["order"]["order_no"]

    response = client.post(f"/api/v1/sales/orders/{order_no}/submit", {}, content_type="application/json")

    assert response.status_code == 409
    assert response.json()["code"] == "stock.insufficient"
    # 庫存不變
    assert StockLevel.objects.get(item=item, location=location).quantity == 10


def test_duplicate_item_in_one_order_is_refused(client, item: Item, location: Location):
    """同一商品不得在同一張單重複列示（AD-22）。"""
    _login(client, "sales6", "sales")
    _receive(item, location, price="10.00", quantity=100, po="G")

    response = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 1},
                {"item_code": item.item_code, "location_code": location.code, "quantity": 2},
            ]
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "lines" in response.json()["field_errors"]


def test_reverse_restores_stock_and_keeps_record(client, item: Item, location: Location):
    """沖銷後庫存回加，原單保留並標示已沖銷（AD-19、AD-28）。"""
    _login(client, "sales7", "sales")
    _receive(item, location, price="10.00", quantity=100, po="H")

    created = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 40}
            ]
        },
        content_type="application/json",
    )
    order_no = created.json()["order"]["order_no"]
    client.post(f"/api/v1/sales/orders/{order_no}/submit", {}, content_type="application/json")
    assert StockLevel.objects.get(item=item, location=location).quantity == 60

    reversed_response = client.post(
        f"/api/v1/sales/orders/{order_no}/reverse", {}, content_type="application/json"
    )

    assert reversed_response.status_code == 200
    assert reversed_response.json()["order"]["status"] == "reversed"
    assert StockLevel.objects.get(item=item, location=location).quantity == 100
    assert StockMovement.objects.filter(purpose=StockMovement.PURPOSE_SALE_REVERSAL).count() == 1


def test_accounting_can_read_margins_but_cannot_create_orders(
    client, item: Item, location: Location
):
    """會計唯讀：可查毛利、不可建立銷貨單（AD-5）。"""
    _login(client, "acct1", "accounting")
    _receive(item, location, price="10.00", quantity=100, po="I")

    read = client.get("/api/v1/sales/margins")
    assert read.status_code == 200

    write = client.post(
        "/api/v1/sales/orders",
        {
            "lines": [
                {"item_code": item.item_code, "location_code": location.code, "quantity": 1}
            ]
        },
        content_type="application/json",
    )
    assert write.status_code == 403
    assert write.json()["code"] == "auth.forbidden"
