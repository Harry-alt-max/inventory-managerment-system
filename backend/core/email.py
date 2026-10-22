"""電子郵件通知（Resend）。

寄信是「附帶的副作用」，不該讓主要流程（入庫、出貨、登入）因此失敗，
因此本模組是全系統**唯一的寄信入口**，並集中處理三件事：

1. **沒有憑證就不寄**：未設定 ``RESEND_API_KEY`` 時直接略過並記錄警告，
   開發環境沒有 Resend 帳號也不會讓流程壞掉。
2. **寄信失敗不影響主要流程**：寄信失敗只記錄，不往上丟例外。
3. **收件者由環境變數決定**：``NOTIFY_EMAILS``，不寫死在程式碼、也不存資料庫
   （Never：不把憑證、收件者名單寫進任何檔案）。

寄信設定（``MAILERS``）由 ``config/settings/base.py`` 依 ``RESEND_API_KEY``
決定：有憑證走 Resend SMTP，沒有就退回 console backend（內容印在伺服器輸出）。
"""
from __future__ import annotations

import logging
from collections.abc import Iterable

from django.conf import settings
from django.core.mail import EmailMessage, mailers

logger = logging.getLogger(__name__)


def is_provider_configured() -> bool:
    """是否已設定寄信服務商憑證（沒有就只記錄、不寄）。"""
    return bool(getattr(settings, "RESEND_API_KEY", ""))


def notification_recipients() -> list[str]:
    """系統通知的預設收件者（來自 ``NOTIFY_EMAILS`` 環境變數）。"""
    return list(getattr(settings, "NOTIFY_EMAILS", []))


def send_notification(
    *,
    subject: str,
    body: str,
    recipients: Iterable[str] | None = None,
) -> bool:
    """寄出通知信。

    - ``recipients`` 為 ``None`` 時使用 ``NOTIFY_EMAILS``。
    - 回傳 ``True`` 代表已成功交給寄信服務；``False`` 代表略過或失敗
      （沒有收件者、沒有憑證、或寄信失敗）。
    - **任何情況都不會丟出例外**：寄信失敗不應讓呼叫端的主要流程失敗。
    """
    targets = [
        address.strip()
        for address in (
            recipients if recipients is not None else notification_recipients()
        )
        if address and address.strip()
    ]
    if not targets:
        logger.info(
            "use_case=send_notification result=skipped reason=no_recipients subject=%s",
            subject,
        )
        return False

    if not is_provider_configured():
        # 沒有憑證時不寄；但把內容記錄下來，讓開發環境看得到「本來要寄什麼」
        logger.warning(
            "use_case=send_notification result=skipped reason=missing_api_key "
            "subject=%s recipients=%s body=%s",
            subject,
            len(targets),
            body.replace("\n", " | "),
        )
        return False

    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=targets,
    )
    try:
        sent = mailers.default.send_messages([message])
    except Exception:
        logger.exception(
            "use_case=send_notification result=failed subject=%s recipients=%s",
            subject,
            len(targets),
        )
        return False

    if sent != 1:
        logger.error(
            "use_case=send_notification result=failed subject=%s sent=%s",
            subject,
            sent,
        )
        return False

    logger.info(
        "use_case=send_notification result=sent subject=%s recipients=%s",
        subject,
        len(targets),
    )
    return True
