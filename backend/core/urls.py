"""/api/v1/ 的 URL 設定。"""
from django.urls import include, path, re_path

from .views import ApiNotFoundView

app_name = "api"

urlpatterns = [
    path("", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("", include(("stock.urls", "stock"), namespace="stock")),
    path("", include(("sales.urls", "sales"), namespace="sales")),
    re_path(r"^.*$", ApiNotFoundView.as_view(), name="not-found"),
]
