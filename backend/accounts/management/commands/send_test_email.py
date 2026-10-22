"""寄一封測試信，確認寄信設定（Resend）是否正確。

用法：

    manage.py send_test_email
    manage.py send_test_email --to someone@example.com

收件者未指定時，取 ``NOTIFY_EMAILS`` 環境變數的第一位。
憑證（``RESEND_API_KEY``）只從環境變數讀取，不會寫入任何檔案（AD-15）。
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from core.email import is_provider_configured, notification_recipients, send_notification


class Command(BaseCommand):
    help = "寄一封測試信，確認 Resend 寄信設定是否正確。"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--to",
            default=None,
            help="收件者 email；未指定時使用 NOTIFY_EMAILS 的第一位。",
        )
        parser.add_argument(
            "--subject",
            default="[庫存管理系統] 測試信",
            help="信件主旨。",
        )

    def handle(self, *args, **options) -> None:
        if not is_provider_configured():
            raise CommandError(
                "未設定 RESEND_API_KEY，無法寄信。"
                "請先設定環境變數 RESEND_API_KEY（例："
                "[Environment]::SetEnvironmentVariable('RESEND_API_KEY','re_xxx','User')）。"
            )

        recipients = [options["to"]] if options.get("to") else notification_recipients()[:1]
        if not recipients:
            raise CommandError(
                "沒有收件者：請用 --to 指定，或設定 NOTIFY_EMAILS 環境變數。"
            )

        body = (
            "這是庫存管理系統的測試信。\n\n"
            "如果你收到這封信，代表 Resend 寄信設定正常。\n"
        )
        sent = send_notification(
            subject=options["subject"],
            body=body,
            recipients=recipients,
        )
        if not sent:
            raise CommandError(
                "寄信未成功。請檢查 RESEND_API_KEY 是否有效、"
                "寄件網域是否已在 Resend 完成驗證、以及 NOTIFY_EMAILS 是否正確。"
            )

        self.stdout.write(self.style.SUCCESS(f"測試信已寄出：{recipients[0]}"))
