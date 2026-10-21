"""領域例外定義（AD-17）。

所有「業務錯誤」都以本檔的例外型別表達，再由單一 DRF exception handler
（``core.handler.exception_handler``）轉為 AD-7 的統一錯誤包絡：

    {"code": ..., "detail": ..., "field_errors": {...}}

約定：
- ``code``      固定、機器可讀的字串（例如 ``stock.insufficient``）
- ``detail``    技術性說明（非使用者可見文案；使用者可見文案由前端 catalog 本地化，AD-33）
- ``field_errors`` 欄位層級錯誤，鍵為欄位名稱
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping


class DomainError(Exception):
    """所有領域例外的基底類別。"""

    code: str = "domain.error"
    default_detail: str = "Domain rule violated."
    status_code: int = 400

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        field_errors: Mapping[str, Iterable[str]] | None = None,
        status_code: int | None = None,
    ) -> None:
        self.detail = detail or self.default_detail
        if code:
            self.code = code
        self.field_errors = {
            key: [str(item) for item in values] for key, values in (field_errors or {}).items()
        }
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class ValidationFailed(DomainError):
    """輸入資料不符合規則。"""

    code = "request.invalid"
    default_detail = "Request validation failed."
    status_code = 400


class ResourceNotFound(DomainError):
    """找不到資源。"""

    code = "resource.not_found"
    default_detail = "Resource not found."
    status_code = 404


class PermissionDenied(DomainError):
    """越權操作。"""

    code = "auth.forbidden"
    default_detail = "Permission denied."
    status_code = 403


class AuthenticationRequired(DomainError):
    """尚未登入或身分失效。"""

    code = "auth.unauthenticated"
    default_detail = "Authentication required."
    status_code = 401


class Conflict(DomainError):
    """狀態衝突。"""

    code = "resource.conflict"
    default_detail = "Resource state conflict."
    status_code = 409


class DuplicateValue(Conflict):
    """唯一性衝突（AD-20 由 DB UNIQUE constraint 落實）。"""

    code = "resource.duplicate"
    default_detail = "Duplicate value."


class InsufficientStock(Conflict):
    """庫存不足。"""

    code = "stock.insufficient"
    default_detail = "Insufficient stock."
    status_code = 409


class DatabaseUnavailable(DomainError):
    """資料庫無法連線。"""

    code = "db.unavailable"
    default_detail = "Database is unavailable."
    status_code = 503


class InvalidCredentials(DomainError):
    """帳號或密碼錯誤。

    AD-19：帳號不存在與密碼錯誤回應同一個 code，避免透露帳號是否存在。
    """

    code = "auth.invalid_credentials"
    default_detail = "Invalid username or password."
    status_code = 401


class AccountLocked(DomainError):
    """帳號因連續登入失敗而被暫時鎖定（AD-19）。

    ``detail`` 會帶上剩餘鎖定秒數（``remaining_seconds=<n>``），供前端顯示
    剩餘鎖定時間；使用者可見文案仍由前端 catalog 本地化（AD-33）。
    """

    code = "auth.locked"
    default_detail = "Account is temporarily locked."
    status_code = 423


class CsrfFailed(DomainError):
    """CSRF 驗證失敗（缺少或不正確的 token）。

    AD-6：session + CSRF 是唯一認證機制，因此寫入型端點必須帶
    ``X-CSRFToken``，否則一律拒絕。
    """

    code = "auth.csrf_failed"
    default_detail = "CSRF verification failed."
    status_code = 403
