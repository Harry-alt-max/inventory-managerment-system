"""accounts app 的 URL 設定（掛在 /api/v1/ 之下）。"""
from django.urls import path

from .auth_views import CsrfView, LoginView, LogoutView, MeView
from .views import HealthView

app_name = "accounts"

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    # 認證（AD-6）：session + CSRF
    path("auth/csrf", CsrfView.as_view(), name="auth-csrf"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/me", MeView.as_view(), name="auth-me"),
]
