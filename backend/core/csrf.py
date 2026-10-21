"""CSRF 驗證（AD-6）。

DRF 的 ``APIView`` 一律是 ``csrf_exempt``，Django 的 ``CsrfViewMiddleware``
不會替它檢查 CSRF；而 DRF 內建的 ``SessionAuthentication`` 只在「已有
session」時才檢查，因此**未登入狀態下的寫入端點（例如登入本身）不會被擋**。

本模組提供明確的 CSRF 檢查，讓登入／登出這類「尚未登入就要寫入」的端點
也能受到保護：

    enforce_csrf(request)   # 失敗時丟出 CsrfFailed（403）

檢查邏輯直接沿用 Django 的 ``CsrfViewMiddleware``（cookie secret 與
``X-CSRFToken`` 標頭的比對、Origin 檢查），只是把「拒絕」改成丟領域例外，
讓錯誤回到單一 exception handler 的統一包絡（AD-17）。
"""
from __future__ import annotations

from django.middleware.csrf import CsrfViewMiddleware

from .exceptions import CsrfFailed


class _CsrfEnforcer(CsrfViewMiddleware):
    """把 Django 的 CSRF 拒絕改成丟出領域例外。"""

    def _reject(self, request, reason):
        raise CsrfFailed(f"CSRF verification failed: {reason}")


def enforce_csrf(request) -> None:
    """驗證請求的 CSRF token；缺少或不正確時丟出 ``CsrfFailed``。

    ``request`` 可以是 DRF 的 ``Request``（會自動取底層的 ``HttpRequest``）。
    """
    django_request = getattr(request, "_request", request)
    enforcer = _CsrfEnforcer(lambda _request: None)
    # 與 DRF SessionAuthentication.enforce_csrf 相同：先讓 META 內的
    # CSRF_COOKIE 與 cookie 同步，再進行檢查。
    enforcer.process_request(django_request)
    reason = enforcer.process_view(django_request, None, (), {})
    if reason:  # pragma: no cover - _reject 已直接丟例外
        raise CsrfFailed(f"CSRF verification failed: {reason}")
