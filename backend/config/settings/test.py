"""測試環境設定（AD-14、AD-23）。

測試「不得連線 AILearn」：此層預設連向獨立的測試資料庫 `AILearn_test`，
測試執行器會在該資料庫上建立 `test_` 前綴的暫存資料庫後刪除。
"""
import os

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("TEST_DB_NAME", "AILearn_test").strip(),
        "USER": os.environ.get("DB_USER", "postgres").strip(),
        "HOST": os.environ.get("DB_HOST", "localhost").strip(),
        "PORT": os.environ.get("DB_PORT", "5432").strip(),
        # 刻意不設定 PASSWORD：密碼由 libpq 依 PGPASSFILE 讀取
        "CONN_MAX_AGE": 0,
        "OPTIONS": {},
    }
}

# 測試期間不快取結果，並使用較短的密碼雜湊以加速
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

# 郵件不外寄：留在記憶體（django.core.mail.outbox）
# Django 6.1 起以 MAILERS 取代 EMAIL_BACKEND（EMAIL_* 於 Django 2028 移除）
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    }
}

# 靜態檔案不需雜湊
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
