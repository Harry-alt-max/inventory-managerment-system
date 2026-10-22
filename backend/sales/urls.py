"""sales app 的 URL 設定（掛在 /api/v1/ 之下）。"""
from django.urls import path

from .views import (
    MarginListView,
    QuoteView,
    SalesOrderDetailView,
    SalesOrderListCreateView,
    SalesOrderReverseView,
    SalesOrderSubmitView,
)

app_name = "sales"

urlpatterns = [
    path("sales/quote", QuoteView.as_view(), name="sales-quote"),
    path("sales/orders", SalesOrderListCreateView.as_view(), name="sales-orders"),
    path("sales/orders/<str:order_no>", SalesOrderDetailView.as_view(), name="sales-order-detail"),
    path(
        "sales/orders/<str:order_no>/submit",
        SalesOrderSubmitView.as_view(),
        name="sales-order-submit",
    ),
    path(
        "sales/orders/<str:order_no>/reverse",
        SalesOrderReverseView.as_view(),
        name="sales-order-reverse",
    ),
    path("sales/margins", MarginListView.as_view(), name="sales-margins"),
]
