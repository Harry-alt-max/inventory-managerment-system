"""catalog app 的 URL 設定（掛在 /api/v1/ 之下）。"""
from django.urls import path

from .views import (
    BatchListCreateView,
    ItemDetailView,
    ItemListCreateView,
    LocationListCreateView,
    WarehouseListCreateView,
)

app_name = "catalog"

urlpatterns = [
    path("items", ItemListCreateView.as_view(), name="item-list"),
    path("items/<str:item_code>", ItemDetailView.as_view(), name="item-detail"),
    path("batches", BatchListCreateView.as_view(), name="batch-list"),
    path("warehouses", WarehouseListCreateView.as_view(), name="warehouse-list"),
    path(
        "warehouses/<str:code>/locations",
        LocationListCreateView.as_view(),
        name="location-list",
    ),
]
