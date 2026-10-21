"""accounts 的 use case（AD-3）。

view 不得直接操作 model：驗證帳號密碼、登入、登出與身分描述都集中在這裡，
view 只負責 HTTP 契約（AD-7）與錯誤包絡（AD-17）。

AD-19 的登入失敗計數與帳號鎖定也在此實作：連續失敗次數存在使用者資料表
（DB），第 5 次失敗鎖定 15 分鐘（UTC 計算），鎖定期間即使密碼正確也拒絕登入。
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.utils import timezone

from core.exceptions import AccountLocked, InvalidCredentials
from core.permissions import role_codes_for_user

from .models import User

logger = logging.getLogger(__name__)

#: 連續登入失敗達此數即鎖定（AD-19）
LOCK_THRESHOLD = 5
#: 鎖定時間長度（AD-19）
LOCK_DURATION = timedelta(minutes=15)


def authenticate_user(username: str, password: str) -> User:
    """驗證帳號與密碼，成功回傳使用者，失敗丟出領域例外。

    - 帳號不存在、密碼錯誤、帳號停用 → ``InvalidCredentials``（同一個 code，
      不透露帳號是否存在，AD-19）；
    - 帳號被鎖定 → ``AccountLocked``（附剩餘鎖定秒數）。
    """
    now = timezone.now()
    user = User.objects.filter(username=username).first()

    if user is not None:
        if user.locked_until is not None:
            if user.locked_until > now:
                remaining = int((user.locked_until - now).total_seconds())
                logger.info(
                    "use_case=authenticate_user actor=%s result=locked remaining_seconds=%s",
                    user.pk,
                    remaining,
                )
                raise AccountLocked(
                    f"Account is locked for {remaining} more seconds.",
                )
            # 鎖定已過期：解除鎖定並歸零失敗次數
            user.locked_until = None
            user.failed_login_count = 0

    if user is None or not user.is_active or not user.check_password(password):
        just_locked = _register_failure(user)
        logger.info(
            "use_case=authenticate_user actor=%s result=%s",
            user.pk if user is not None else "anonymous",
            "locked" if just_locked else "invalid_credentials",
        )
        if just_locked:
            raise AccountLocked(
                f"Account is locked for {int(LOCK_DURATION.total_seconds())} more seconds.",
            )
        raise InvalidCredentials()

    user.failed_login_count = 0
    user.locked_until = None
    user.save(update_fields=["failed_login_count", "locked_until"])
    logger.info("use_case=authenticate_user actor=%s result=success", user.pk)
    return user


def _register_failure(user: User | None) -> bool:
    """累加連續失敗次數；達門檻即鎖定（AD-19）。

    帳號不存在時無從計數（不建立任何影子資料）。

    回傳 ``True`` 表示這次失敗刚好觸發鎖定。
    """
    if user is None:
        return False

    user.failed_login_count += 1
    fields = ["failed_login_count"]
    just_locked = False
    if user.failed_login_count >= LOCK_THRESHOLD:
        user.locked_until = timezone.now() + LOCK_DURATION
        fields.append("locked_until")
        just_locked = True
    user.save(update_fields=fields)
    return just_locked


def perform_login(request: Any, user: User) -> None:
    """建立 session（AD-6：session + CSRF 是唯一認證機制）。"""
    django_login(_django_request(request), user)
    logger.info("use_case=perform_login actor=%s result=success", user.pk)


def perform_logout(request: Any) -> None:
    """結束 session（AD-6）。"""
    django_request = _django_request(request)
    actor_id = getattr(getattr(django_request, "user", None), "pk", None)
    django_logout(django_request)
    logger.info("use_case=perform_logout actor=%s result=success", actor_id)


def _django_request(request: Any) -> Any:
    """取出底層的 Django ``HttpRequest``。

    DRF 的 ``Request`` 是包裝層；session、user 與 META 的真正來源是底層的
    ``HttpRequest``，登入／登出一律作用在它上面（避免 DRF 以匿名使用者
    覆寫底層的 user）。
    """
    return getattr(request, "_request", request)


def describe_user(user: User) -> dict[str, Any]:
    """描述登入者身分：識別碼、帳號、顯示名稱與角色代碼清單。

    角色以**代碼**回傳（AD-33：使用者可見文案由前端 message catalog 本地化）。
    """
    display_name = user.get_full_name().strip() or user.get_username()
    return {
        "id": user.pk,
        "username": user.get_username(),
        "display_name": display_name,
        "roles": role_codes_for_user(user),
    }
