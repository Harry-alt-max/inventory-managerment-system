"""認證端點（AD-6、AD-19）。

掛在 ``/api/v1/auth/`` 之下：

- ``GET  /api/v1/auth/csrf``   → 發放 CSRF cookie 並回傳 token
- ``POST /api/v1/auth/login``  → 帳號密碼登入（需要 ``X-CSRFToken``）
- ``POST /api/v1/auth/logout`` → 結束 session（需要 ``X-CSRFToken``）
- ``GET  /api/v1/auth/me``     → 目前登入者（未登入回 401）

view 只做 HTTP 契約與錯誤包絡；驗證、登入與身分描述都在
``accounts.services``（AD-3）。
"""
from __future__ import annotations

from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.csrf import enforce_csrf
from core.exceptions import ValidationFailed
from core.permissions import RequireAuthenticated

from .services import authenticate_user, describe_user, perform_login, perform_logout


class CsrfView(APIView):
    """發放 CSRF token（AD-6）。

    回應同時帶上 ``Set-Cookie: csrftoken=...`` 與 JSON 內的 token，
    前端以 ``X-CSRFToken`` 標頭帶回。
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return Response({"csrf_token": get_token(request)})


class LoginView(APIView):
    """以帳號密碼登入（AD-6、AD-19）。

    - 成功：200 ``{"user": {...}}``（含角色代碼清單）
    - 密碼錯誤／帳號不存在／帳號停用：401 ``auth.invalid_credentials``
    - 帳號鎖定：423 ``auth.locked``（detail 帶剩餘鎖定秒數）
    - 缺少 CSRF token 或 token 不正確：403 ``auth.csrf_failed``
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request, *args, **kwargs):
        enforce_csrf(request)

        username = str(request.data.get("username") or "").strip()
        password = str(request.data.get("password") or "")

        field_errors: dict[str, list[str]] = {}
        if not username:
            field_errors["username"] = ["This field is required."]
        if not password:
            field_errors["password"] = ["This field is required."]
        if field_errors:
            raise ValidationFailed(field_errors=field_errors)

        user = authenticate_user(username, password)
        perform_login(request, user)
        return Response({"user": describe_user(user)})


class LogoutView(APIView):
    """結束 session（AD-6）。

    - 成功：200 ``{"status": "signed_out"}``（冪等：未登入也回 200）
    - 缺少或不正確的 CSRF token：403 ``auth.csrf_failed``
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 已登入時 DRF 的 SessionAuthentication 已做過 CSRF 檢查；未登入時
        # 由這裡補上（AD-6：寫入型端點一律要求 CSRF token）。
        enforce_csrf(request)
        perform_logout(request)
        return Response({"status": "signed_out"})


class MeView(APIView):
    """回傳目前登入者（AD-6）。

    - 已登入：200 ``{"user": {...}}``
    - 未登入：401 ``auth.unauthenticated``
    """

    permission_classes = [RequireAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"user": describe_user(request.user)})
