"""stock app 的 URL 設定（掛在 /api/v1/ 之下）。"""
from django.urls import path

from .views import StockInboundView, StockListView, StockMovementListView

app_name = "stock"

urlpatterns = [
    path("stock", StockListView.as_view(), name="stock-list"),
    path("stock/inbound", StockInboundView.as_view(), name="stock-inbound"),
    path("stock/movements", StockMovementListView.as_view(), name="stock-movements"),
]
