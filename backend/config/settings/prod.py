"""正式環境設定（AD-23）。

正式環境的必要值一律由環境變數注入，缺少任何一項都在「啟動時」直接失敗，
不得退回預設值，也不得沿用開發層的 DEBUG=True。

必要環境變數：
- SECRET_KEY      正式環境的金鑰
- ALLOWED_HOSTS   允許的主機（逗號分隔）
- DB_NAME         正式環境的資料庫名稱（正式需明確指定，不使用開發的 AILearn）

憑證（PGPASSFILE）由 base 層檢查。
"""
import os

from django.core.exceptions import ImproperlyConfigured


def _require_env(name: str, hint: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"缺少必要的環境變數 {name}：{hint}")
    return value


# 先檢查正式環境的必要變數，缺值時直接指出缺哪一個（不退回預設值）。
SECRET_KEY = _require_env(
    "SECRET_KEY",
    "正式環境金鑰，必須由環境變數注入，不得使用預設值。",
)
_ALLOWED_HOSTS = _require_env(
    "ALLOWED_HOSTS",
    "正式環境允許的主機清單，以逗號分隔，例如 example.com,10.0.0.5。",
)
_DB_NAME = _require_env(
    "DB_NAME",
    "正式環境資料庫名稱；正式環境必須明確指定，不沿用開發用的 AILearn。",
)

from .base import *  # noqa: E402,F401,F403

DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in _ALLOWED_HOSTS.split(",") if host.strip()]

DATABASES["default"]["NAME"] = _DB_NAME  # noqa: F405

# 正式環境的靜態檔案以雜湊檔名供應；缺檔時不得靜默回 404 而應直接失敗
WHITE_NOISE_AUTOREFRESH = False
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# 安全強化
# SECURE_SSL 預設關閉：本機以 waitress + WhiteNoise 走純 HTTP 部署（AD-23 的本機正式環境），
# 開啟後會被 301 轉到沒有任何終端的 https，且 cookie 也不再送出。
SECURE_SSL = os.environ.get("SECURE_SSL", "0").strip().lower() not in {"0", "false", "no"}
SECURE_SSL_REDIRECT = SECURE_SSL
SESSION_COOKIE_SECURE = SECURE_SSL
CSRF_COOKIE_SECURE = SECURE_SSL
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
