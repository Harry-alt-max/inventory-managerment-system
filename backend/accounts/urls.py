"""accounts app 的 URL 設定（掛在 /api/v1/ 之下）。"""
from django.urls import path

from .views import HealthView

app_name = "accounts"

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
]
