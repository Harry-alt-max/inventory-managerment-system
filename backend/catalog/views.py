"""catalog app 的 API 檢視。

view 只做 HTTP 契約（AD-7）與錯誤包絡（AD-17）；所有寫入都交給
``catalog.services`` 的 use case（AD-3），所有權限都在 view 層宣告（AD-5）。

端點（掛在 ``/api/v1/`` 之下）：

- ``GET  /api/v1/items``                     商品清單（``query`` 名稱關鍵字）
- ``POST /api/v1/items``                     建立商品主檔
- ``GET  /api/v1/items/<item_code>``         商品明細（含其採購批次）
- ``GET  /api/v1/batches``                   採購批次清單
- ``POST /api/v1/batches``                   建立採購批次
- ``GET  /api/v1/warehouses``               倉庫清單
- ``POST /api/v1/warehouses``               建立倉庫
- ``GET  /api/v1/warehouses/<code>/locations`` 某倉庫的庫存位置
- ``POST /api/v1/warehouses/<code>/locations`` 建立庫存位置
"""
from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from decimal import Decimal
from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import (
    PERM_MANAGE_BATCH,
    PERM_MANAGE_ITEM,
    PERM_MANAGE_WAREHOUSE,
    PERM_VIEW_BATCH,
    PERM_VIEW_CATALOG,
    PERM_VIEW_STOCK,
    require_permissions,
)

from . import services


def _actor(request: Request) -> str:
    """取得操作人員代號（AD-32：actor 為顯式參數，不使用 thread-local）。"""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return "anonymous"
    return user.get_username()


def _money(value: Decimal | None) -> str:
    """金額輸出固定小數兩位（AD-9）。"""
    if value is None:
        return "0.00"
    return f"{value:.2f}"


def _timestamp(value: datetime | None) -> str | None:
    """時間戳一律 UTC（ISO 8601，含時區，AD-10）。"""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt_timezone.utc)
    return value.astimezone(dt_timezone.utc).isoformat().replace("+00:00", "Z")


def _serialize_item(item) -> dict[str, Any]:
    return {
        "item_code": item.item_code,
        "name": item.name,
        "supplier_name": item.supplier_name,
        "suggested_price": _money(item.suggested_price),
        "expected_margin": _money(item.expected_margin),
        "created_at": _timestamp(item.created_at),
        "updated_at": _timestamp(item.updated_at),
    }


def _serialize_batch(batch) -> dict[str, Any]:
    return {
        "po_number": batch.po_number,
        "item_code": batch.item.item_code,
        "item_name": batch.item.name,
        "supplier_name": batch.supplier_name,
        "unit_price": _money(batch.unit_price),
        "quantity": batch.quantity,
        "total": _money(batch.total),
        "received_at": batch.received_at.isoformat(),
        "created_at": _timestamp(batch.created_at),
    }


def _serialize_warehouse(warehouse) -> dict[str, Any]:
    return {"code": warehouse.code, "name": warehouse.name}


def _serialize_location(location) -> dict[str, Any]:
    return {
        "code": location.code,
        "name": location.name,
        "warehouse_code": location.warehouse.code,
    }


class ItemListCreateView(APIView):
    """商品清單與建立（FR-4、FR-5）。"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [require_permissions(PERM_MANAGE_ITEM)()]
        return [require_permissions(PERM_VIEW_CATALOG)()]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", "")
        items = services.list_items(query=query)
        return Response({"items": [_serialize_item(item) for item in items]})

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        item = services.create_item(
            actor=_actor(request),
            name=payload.get("name"),
            supplier_name=payload.get("supplier_name"),
            suggested_price=payload.get("suggested_price"),
            expected_margin=payload.get("expected_margin"),
        )
        return Response({"item": _serialize_item(item)}, status=201)


class ItemDetailView(APIView):
    """商品明細（含其採購批次）。"""

    permission_classes = [require_permissions(PERM_VIEW_CATALOG)()]

    def get(self, request, item_code: str, *args, **kwargs):
        item = services.get_item(item_code=item_code)
        batches = services.list_batches_of_item(item=item)
        payload = _serialize_item(item)
        payload["batches"] = [_serialize_batch(batch) for batch in batches]
        return Response({"item": payload})


class BatchListCreateView(APIView):
    """採購批次清單與建立（FR-9）。"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [require_permissions(PERM_MANAGE_BATCH)()]
        return [require_permissions(PERM_VIEW_BATCH)()]

    def get(self, request, *args, **kwargs):
        item_code = request.query_params.get("item_code", "")
        batches = services.list_batches(item_code=item_code)
        return Response({"batches": [_serialize_batch(batch) for batch in batches]})

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        batch = services.create_batch(
            actor=_actor(request),
            item_code=payload.get("item_code"),
            po_number=payload.get("po_number"),
            supplier_name=payload.get("supplier_name"),
            unit_price=payload.get("unit_price"),
            quantity=payload.get("quantity"),
            received_at=payload.get("received_at"),
        )
        return Response({"batch": _serialize_batch(batch)}, status=201)


class WarehouseListCreateView(APIView):
    """倉庫清單與建立（FR-10）。"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [require_permissions(PERM_MANAGE_WAREHOUSE)()]
        return [require_permissions(PERM_VIEW_STOCK)()]

    def get(self, request, *args, **kwargs):
        warehouses = services.list_warehouses()
        return Response(
            {"warehouses": [_serialize_warehouse(warehouse) for warehouse in warehouses]}
        )

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        warehouse = services.create_warehouse(
            actor=_actor(request),
            code=payload.get("code"),
            name=payload.get("name"),
        )
        return Response({"warehouse": _serialize_warehouse(warehouse)}, status=201)


class LocationListCreateView(APIView):
    """某倉庫的庫存位置清單與建立（FR-10）。"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [require_permissions(PERM_MANAGE_WAREHOUSE)()]
        return [require_permissions(PERM_VIEW_STOCK)()]

    def get(self, request, code: str, *args, **kwargs):
        locations = services.list_locations(warehouse_code=code)
        return Response(
            {"locations": [_serialize_location(location) for location in locations]}
        )

    def post(self, request, code: str, *args, **kwargs):
        payload = request.data or {}
        location = services.create_location(
            actor=_actor(request),
            warehouse_code=code,
            code=payload.get("code"),
            name=payload.get("name"),
        )
        return Response({"location": _serialize_location(location)}, status=201)

