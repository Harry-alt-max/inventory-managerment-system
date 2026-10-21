"""開發環境設定（AD-23）。

開發環境連線本機 `AILearn`，憑證由 PGPASSFILE 指向的 pgpass.conf 提供。
"""
from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "0.0.0.0",  # noqa: S104 - 僅開發環境的 runserver 便利設定
]

# 開發時 Django 應能顯示除錯頁面，但不得洩漏憑證
INTERNAL_IPS = ["127.0.0.1"]
