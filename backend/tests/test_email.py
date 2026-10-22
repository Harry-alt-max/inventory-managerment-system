"""電子郵件通知（Resend）的行為驗證。

覆蓋三個重點：

1. 沒有 ``RESEND_API_KEY`` 時**不寄**（開發環境沒有 Resend 帳號也能運作）
2. 沒有收件者時**不寄**
3. 有憑證時寄出信件（測試環境走 locmem backend，信件留在 ``mail.outbox``）
4. 入庫（``receive_stock``）會在交易提交後寄出通知信
"""
from __future__ import annotations

import pytest
from django.core import mail
from django.db import transaction

from catalog.models import Batch, Item, Location, Warehouse
from core.email import is_provider_configured, notification_recipients, send_notification
from stock.services import receive_stock

pytestmark = pytest.mark.django_db


@pytest.fixture
def warehouse() -> Warehouse:
    return Warehouse.objects.create(code="A1", name="A 倉")


@pytest.fixture
def location(warehouse: Warehouse) -> Location:
    return Location.objects.create(warehouse=warehouse, code="A-03", name="A 倉 03 區")


@pytest.fixture
def item() -> Item:
    return Item.objects.create(
        name="測試螺絲 M8x40",
        supplier_name="測試供應商",
        suggested_price="12.50",
        expected_margin="3.00",
    )


@pytest.fixture
def batch(item: Item) -> Batch:
    return Batch.objects.create(
        item=item,
        supplier_name="測試供應商",
        unit_price="12.50",
        quantity=100,
        received_at="2026-10-21",
    )


def test_no_api_key_skips_sending(settings):
    """沒有憑證時不寄信，只回 False。"""
    settings.RESEND_API_KEY = ""
    settings.NOTIFY_EMAILS = ["ops@example.com"]

    sent = send_notification(subject="測試", body="內容")

    assert sent is False
    assert mail.outbox == []


def test_no_recipients_skips_sending(settings):
    """沒有收件者時不寄信。"""
    settings.RESEND_API_KEY = "re_test_key"
    settings.NOTIFY_EMAILS = []

    sent = send_notification(subject="測試", body="內容")

    assert sent is False
    assert mail.outbox == []


def test_sends_when_configured(settings):
    """有憑證與收件者時寄出信件。"""
    settings.RESEND_API_KEY = "re_test_key"
    settings.NOTIFY_EMAILS = ["ops@example.com", "manager@example.com"]
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"

    sent = send_notification(subject="測試主旨", body="測試內容")

    assert sent is True
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.subject == "測試主旨"
    assert message.body == "測試內容"
    assert message.to == ["ops@example.com", "manager@example.com"]
    assert message.from_email == "noreply@example.com"


def test_explicit_recipients_override_default(settings):
    """指定收件者時不使用 NOTIFY_EMAILS。"""
    settings.RESEND_API_KEY = "re_test_key"
    settings.NOTIFY_EMAILS = ["ops@example.com"]

    sent = send_notification(
        subject="指定收件者",
        body="內容",
        recipients=["someone@example.com"],
    )

    assert sent is True
    assert mail.outbox[0].to == ["someone@example.com"]


def test_inbound_triggers_notification(
    django_capture_on_commit_callbacks, settings, item, batch, location
):
    """入庫成功後寄出通知信。"""
    settings.RESEND_API_KEY = "re_test_key"
    settings.NOTIFY_EMAILS = ["ops@example.com"]

    with django_capture_on_commit_callbacks(execute=True):
        receive_stock(
            actor="demo_warehouse",
            item_code=item.item_code,
            location_code=location.code,
            batch_po_number=batch.po_number,
            quantity=5,
        )

    assert len(mail.outbox) == 1
    assert "入庫通知" in mail.outbox[0].subject
    assert "5" in mail.outbox[0].body


def test_inbound_does_not_notify_when_rolled_back(
    django_capture_on_commit_callbacks, settings, item, batch, location
):
    """交易回滾時不寄信（通知在 transaction.on_commit 觸發）。"""
    settings.RESEND_API_KEY = "re_test_key"
    settings.NOTIFY_EMAILS = ["ops@example.com"]

    with django_capture_on_commit_callbacks(execute=True):
        with pytest.raises(RuntimeError):
            with transaction.atomic():
                receive_stock(
                    actor="demo_warehouse",
                    item_code=item.item_code,
                    location_code=location.code,
                    batch_po_number=batch.po_number,
                    quantity=5,
                )
                raise RuntimeError("rollback")

    assert mail.outbox == []


def test_helpers_read_settings(settings):
    """工具函式反映設定內容。"""
    settings.RESEND_API_KEY = ""
    settings.NOTIFY_EMAILS = ["a@example.com", "b@example.com"]

    assert is_provider_configured() is False
    assert notification_recipients() == ["a@example.com", "b@example.com"]
