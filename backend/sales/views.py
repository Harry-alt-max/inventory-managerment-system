"""銷貨 API 檢視（只做 HTTP 契約與錯誤包絡，邏輯在 services）。"""
from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import (
    PERM_CREATE_SALES_ORDER,
    PERM_VIEW_MARGIN,
    PERM_VIEW_SALES_ORDER,
    require_permissions,
)

from . import services


def _actor(request: Request) -> str:
    """操作人員代號（AD-32：actor 為顯式參數）。"""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return "anonymous"
    return user.get_username()


def _serialize_order(order) -> dict:
    return {
        "order_no": order.order_no,
        "status": order.status,
        "status_label": order.get_status_display(),
        "discount_rate": str(order.discount_rate),
        "total_amount": str(order.total_amount),
        "discount_amount": str(order.total_discount),
        "total_paid": str(order.total_paid),
        "total_cost": str(order.total_cost),
        "total_margin": str(order.total_margin),
        "created_by": order.created_by,
        "created_at": order.created_at.isoformat(),
        "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
        "note": order.note,
        "lines": [
            {
                "item_code": line.item.item_code,
                "item_name": line.item.name,
                "location_code": line.location.code,
                "quantity": line.quantity,
                "unit_price": str(line.unit_price),
                "subtotal": str(line.subtotal),
                "cost": str(line.cost),
                "consumptions": [
                    {
                        "po_number": consumption.batch.po_number,
                        "quantity": consumption.quantity,
                        "unit_price": str(consumption.unit_price),
                        "cost": str(consumption.cost),
                    }
                    for consumption in line.consumptions.all()
                ],
            }
            for line in order.lines.all()
        ],
    }


class QuoteView(APIView):
    """報價試算（唯讀，不寫入，AD-26）。"""

    permission_classes = [require_permissions(PERM_VIEW_SALES_ORDER)]

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        result = services.quote(
            lines=payload.get("lines") or [],
            discount_rate=payload.get("discount_rate") or 0,
        )
        return Response(result)


class SalesOrderListCreateView(APIView):
    """銷貨單清單與建立（草稿）。"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [require_permissions(PERM_CREATE_SALES_ORDER)()]
        return [require_permissions(PERM_VIEW_SALES_ORDER)()]

    def get(self, request, *args, **kwargs):
        orders = services.list_orders(
            order_no=request.query_params.get("order_no", ""),
            date_from=request.query_params.get("date_from", ""),
            date_to=request.query_params.get("date_to", ""),
        )
        return Response({"orders": [_serialize_order(order) for order in orders]})

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        order = services.create_order(
            actor=_actor(request),
            lines=payload.get("lines") or [],
            discount_rate=payload.get("discount_rate") or 0,
            note=str(payload.get("note") or ""),
        )
        return Response({"order": _serialize_order(order)}, status=201)


class SalesOrderDetailView(APIView):
    """銷貨單明細。"""

    permission_classes = [require_permissions(PERM_VIEW_SALES_ORDER)]

    def get(self, request, order_no: str, *args, **kwargs):
        order = services.get_order(order_no)
        return Response({"order": _serialize_order(order)})


class SalesOrderSubmitView(APIView):
    """送出銷貨單：扣減庫存並寫入異動與批次消耗。"""

    permission_classes = [require_permissions(PERM_CREATE_SALES_ORDER)]

    def post(self, request, order_no: str, *args, **kwargs):
        order = services.submit_order(actor=_actor(request), order_no=order_no)
        return Response({"order": _serialize_order(order)})


class SalesOrderReverseView(APIView):
    """沖銷銷貨單：庫存回加並留下沖銷紀錄。"""

    permission_classes = [require_permissions(PERM_CREATE_SALES_ORDER)]

    def post(self, request, order_no: str, *args, **kwargs):
        order = services.reverse_order(actor=_actor(request), order_no=order_no)
        return Response({"order": _serialize_order(order)})


class MarginListView(APIView):
    """毛利查核清單（會計唯讀，AD-5）。"""

    permission_classes = [require_permissions(PERM_VIEW_MARGIN)]

    def get(self, request, *args, **kwargs):
        orders = services.list_orders(
            order_no=request.query_params.get("order_no", ""),
            date_from=request.query_params.get("date_from", ""),
            date_to=request.query_params.get("date_to", ""),
        )
        return Response({"orders": [_serialize_order(order) for order in orders]})
