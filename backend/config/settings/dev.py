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

# 開發時前端由 Vite dev server（:5173）提供，API 以 proxy 轉送 Django（:8000）。
# 瀏覽器送出的 Origin 仍是 :5173，與 Django 看到的 Host 不同，因此必須把
# 開發用 origin 列為信任來源，否則 CSRF 的 Origin 檢查會擋掉登入（AD-6）。
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

# 示範模式：允許「選角色直接進入」（POST /api/v1/auth/login-as）。
# 正式環境的 base 層預設關閉（AD-23：正式環境不得有便利的預設行為）。
DEMO_ROLE_LOGIN = True
