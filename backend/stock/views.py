"""庫存 API 檢視（只做 HTTP 契約與錯誤包絡，邏輯在 services）。"""
from __future__ import annotations

from django.db.models import Sum
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import (
    PERM_CREATE_STOCK_INBOUND,
    PERM_VIEW_STOCK,
    require_permissions,
)

from . import services


def _actor(request: Request) -> str:
    """操作人員代號（AD-32：actor 為顯式參數）。"""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return "anonymous"
    return user.get_username()


def _serialize_level(level) -> dict:
    return {
        "item_code": level.item.item_code,
        "item_name": level.item.name,
        "location_code": level.location.code,
        "location_name": level.location.name,
        "warehouse_code": level.location.warehouse.code,
        "warehouse_name": level.location.warehouse.name,
        "quantity": level.quantity,
        "updated_at": level.updated_at.isoformat(),
    }


def _serialize_movement(movement) -> dict:
    return {
        "id": movement.id,
        "item_code": movement.item.item_code,
        "item_name": movement.item.name,
        "location_code": movement.location.code,
        "warehouse_code": movement.location.warehouse.code,
        "batch_po_number": movement.batch.po_number if movement.batch_id else None,
        "quantity": movement.quantity,
        "purpose": movement.purpose,
        "actor_username": movement.actor_username,
        "occurred_at": movement.occurred_at.isoformat(),
        "note": movement.note,
    }


class StockListView(APIView):
    """庫存現況清單。"""

    permission_classes = [require_permissions(PERM_VIEW_STOCK)]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", "")
        levels = services.list_stock(query=query)
        return Response({"stock": [_serialize_level(level) for level in levels]})


class StockInboundView(APIView):
    """入庫作業（AD-11）。"""

    permission_classes = [require_permissions(PERM_CREATE_STOCK_INBOUND)]

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        quantity = payload.get("quantity")
        movement = services.receive_stock(
            actor=_actor(request),
            item_code=payload.get("item_code"),
            location_code=payload.get("location_code"),
            batch_po_number=payload.get("batch_po_number"),
            quantity=int(quantity) if str(quantity or "").strip().isdigit() else quantity,
            note=str(payload.get("note") or ""),
        )
        return Response({"movement": _serialize_movement(movement)}, status=201)


class StockMovementListView(APIView):
    """庫存異動紀錄查詢。"""

    permission_classes = [require_permissions(PERM_VIEW_STOCK)]

    def get(self, request, *args, **kwargs):
        movements = services.list_movements(
            item_code=request.query_params.get("item_code", ""),
            purpose=request.query_params.get("purpose", ""),
        )
        return Response({"movements": [_serialize_movement(m) for m in movements]})
