"""建立業務編號用的 PostgreSQL sequence（AD-8）。

商品編號（``INV-`` + 6 碼）取自全域 sequence；採購批次流水號（``PO-YYYYMMDD-NNN``）
改為「每日一個 sequence」，序號在同一天內遞增且不重複（見 ``catalog/codes.py``）。
"""
from django.db import migrations


CREATE_ITEM_SEQUENCE = """
CREATE SEQUENCE IF NOT EXISTS catalog_item_code_seq START 1 INCREMENT 1;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(CREATE_ITEM_SEQUENCE, migrations.RunSQL.noop),
    ]
