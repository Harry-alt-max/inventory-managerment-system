"""業務編號的配置（AD-8）。

商品編號 ``INV-`` + 6 碼、採購批次流水號 ``PO-YYYYMMDD-NNN`` 皆由
**資料庫 sequence** 產生（sequence 由 migration 以 ``CREATE SEQUENCE IF NOT EXISTS``
建立，見 ``catalog/migrations/0001_initial.py``），建立後不可修改，序號永不使用。

本模組只提供「取號」能力；取到的號碼是唯一性防線的一半，另一半是資料庫的
UNIQUE constraint（AD-20）。
"""
from __future__ import annotations

from django.db import connection
from django.utils import timezone

#: 商品編號流水（``INV-`` + 6 碼）
ITEM_CODE_SEQUENCE = "catalog_item_code_seq"
#: 採購批次流水號流水（``PO-YYYYMMDD-NNN``）
PO_NUMBER_SEQUENCE = "catalog_po_number_seq"

#: 商品編號前綴
ITEM_CODE_PREFIX = "INV-"
#: 採購批次流水號前綴
PO_NUMBER_PREFIX = "PO-"


def _nextval(sequence_name: str) -> int:
    """取 sequence 的下一個值。"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval(%s)", [sequence_name])
        row = cursor.fetchone()
    return int(row[0])


def allocate_item_code() -> str:
    """配置商品編號：``INV-`` + 6 碼流水號（AD-8）。"""
    value = _nextval(ITEM_CODE_SEQUENCE)
    return f"{ITEM_CODE_PREFIX}{value:06d}"


def allocate_po_number() -> str:
    """配置採購批次流水號：``PO-YYYYMMDD-NNN``（AD-8）。

    日期部分為**建立當日**（業務日期，顯示時區 Asia/Taipei，AD-10）；
    序號取自「每日一個 sequence」，因此同一天內遞增且不重複，也不會與其他日期撞號。
    """
    business_date = timezone.localdate()
    # sequence 名稱由日期組成（非使用者輸入），DDL 的識別子無法參數化，故以 f-string 組裝。
    sequence_name = f"catalog_po_number_seq_{business_date:%Y%m%d}"
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SEQUENCE IF NOT EXISTS "{sequence_name}"')
        cursor.execute("SELECT nextval(%s)", [sequence_name])
        value = int(cursor.fetchone()[0])
    return f"{PO_NUMBER_PREFIX}{business_date:%Y%m%d}-{value:03d}"
