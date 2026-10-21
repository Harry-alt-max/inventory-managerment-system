"""單一 DRF exception handler（AD-7、AD-17）。

所有 API 錯誤都由此處統一轉成：

    {"code": ..., "detail": ..., "field_errors": {...}}

DRF 預設的 handler 會把 validation error 回成 ``{"field": ["msg"]}``，
破壞統一包絡，因此這裡改寫回應形狀。
"""
from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import DomainError

logger = logging.getLogger(__name__)

# 依例外型別指定機器可讀代碼；順序有意義（由具體到一般）
_CODE_BY_EXCEPTION: list[tuple[type[Exception], str]] = [
    (drf_exceptions.ValidationError, "request.invalid"),
    (drf_exceptions.ParseError, "request.invalid"),
    (drf_exceptions.AuthenticationFailed, "auth.unauthenticated"),
    (drf_exceptions.NotAuthenticated, "auth.unauthenticated"),
    (drf_exceptions.PermissionDenied, "auth.forbidden"),
    (drf_exceptions.NotFound, "resource.not_found"),
    (drf_exceptions.MethodNotAllowed, "request.method_not_allowed"),
    (drf_exceptions.NotAcceptable, "request.not_acceptable"),
    (drf_exceptions.UnsupportedMediaType, "request.unsupported_media_type"),
    (drf_exceptions.Throttled, "request.throttled"),
]

_CODE_BY_STATUS: dict[int, str] = {
    400: "request.invalid",
    401: "auth.unauthenticated",
    403: "auth.forbidden",
    404: "resource.not_found",
    405: "request.method_not_allowed",
    406: "request.not_acceptable",
    409: "resource.conflict",
    415: "request.unsupported_media_type",
    429: "request.throttled",
    500: "system.internal_error",
    503: "service.unavailable",
}

_DETAIL_BY_STATUS: dict[int, str] = {
    400: "Request validation failed.",
    401: "Authentication required.",
    403: "Permission denied.",
    404: "Resource not found.",
    405: "Method not allowed.",
    409: "Resource state conflict.",
    500: "Internal server error.",
    503: "Service unavailable.",
}


def error_response(
    code: str,
    detail: str,
    *,
    status: int = 400,
    field_errors: dict[str, list[str]] | None = None,
) -> Response:
    """建立統一錯誤包絡的回應。"""
    return Response(
        {
            "code": code,
            "detail": detail,
            "field_errors": field_errors or {},
        },
        status=status,
    )


def _code_for(exc: Exception, status: int) -> str:
    for exc_type, code in _CODE_BY_EXCEPTION:
        if isinstance(exc, exc_type):
            return code
    default_code = getattr(exc, "default_code", None)
    if isinstance(default_code, str) and default_code:
        return default_code
    return _CODE_BY_STATUS.get(status, "request.error")


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """DRF 統一例外處理器。"""
    if isinstance(exc, DomainError):
        return error_response(
            exc.code,
            exc.detail,
            status=exc.status_code,
            field_errors=exc.field_errors,
        )

    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:
        # 未預期的錯誤：記錄後以統一包絡回 500，不洩漏內部細節
        logger.error("未預期的錯誤：%r", exc, exc_info=exc)
        return error_response(
            "system.internal_error",
            "Internal server error.",
            status=500,
        )

    status = response.status_code
    code = _code_for(exc, status)
    data = response.data

    # 框架例外一律使用固定的技術性說明（不隨 Django 語系改變）：
    # 使用者可見文案由前端 message catalog 依 code 本地化（AD-33）。
    detail = _DETAIL_BY_STATUS.get(status, "Request failed.")

    field_errors: dict[str, list[str]] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "detail":
                continue
            field_errors[key] = (
                [str(item) for item in value] if isinstance(value, (list, tuple)) else [str(value)]
            )
    elif isinstance(data, (list, tuple)):
        field_errors = {"non_field_errors": [str(item) for item in data]}

    return error_response(code, detail, status=status, field_errors=field_errors)
