"""基礎設定：所有環境共用的部分。

分層原則（AD-23）：base 只放「四層共用」的值，任何環境專屬的東西
（DEBUG、SECRET_KEY、ALLOWED_HOSTS、資料庫名稱）都由 dev／test／prod 決定。

安全原則（AD-15）：本檔案不含任何密碼、密鑰或憑證。
PostgreSQL 憑證只由 ``PGPASSFILE`` 指向的 pgpass.conf 提供（libpq 自行讀取），
因此 DATABASES 一律不設定 ``PASSWORD``。
"""
import os
import warnings
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

# backend/ 為 BASE_DIR，專案根目錄為 PROJECT_ROOT
BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent


def require_env(name: str, hint: str) -> str:
    """取環境變數；缺值時直接失敗，不退回預設值（AD-23）。"""
    value = os.environ.get(name)
    if not value or not value.strip():
        raise ImproperlyConfigured(f"缺少必要的環境變數 {name}：{hint}")
    return value.strip()


# ---------------------------------------------------------------------------
# 憑證來源（AD-15）：只認 pgpass.conf，不接受程式碼或檔案內的密碼
# ---------------------------------------------------------------------------
PGPASSFILE = require_env(
    "PGPASSFILE",
    "PostgreSQL 憑證檔（pgpass.conf）的完整路徑；連線密碼只由此檔提供。",
)
if not Path(PGPASSFILE).is_file():
    raise ImproperlyConfigured(
        f"PGPASSFILE 指向的檔案不存在：{PGPASSFILE}；請先建立 pgpass.conf。"
    )

# ---------------------------------------------------------------------------
# 核心安全設定
# ---------------------------------------------------------------------------
# SECRET_KEY 只從環境變數注入；開發時若未注入則使用「本次行程的暫時鍵」，
# 不得將任何固定金鑰寫進版控（Never：不把憑證、密碼或金鑰寫進任何檔案）。
_secret_key = os.environ.get("SECRET_KEY", "").strip()
if not _secret_key:
    _secret_key = get_random_secret_key()
    warnings.warn(
        "未設定 SECRET_KEY 環境變數，已改用本次行程的暫時金鑰（開發用）。",
        RuntimeWarning,
        stacklevel=2,
    )
SECRET_KEY = _secret_key

DEBUG = False
ALLOWED_HOSTS: list[str] = []

# 「選角色直接進入」的示範模式（POST /api/v1/auth/login-as）。
# 預設關閉；僅開發環境的 settings/dev.py 開啟，正式環境必須由環境變數明確啟用。
DEMO_ROLE_LOGIN = (
    os.environ.get("DEMO_ROLE_LOGIN", "").strip().lower() in {"1", "true", "yes"}
)

# ---------------------------------------------------------------------------
# 應用程式
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
    "accounts",
    "catalog",
    "stock",
    "sales",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 使用者模型放在 accounts app（AD-5：權限以 Django auth + Group/Permission 落地）
AUTH_USER_MODEL = "accounts.User"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# 資料庫（AD-15：單一 PostgreSQL 實例的單一 schema，不在檔案中放密碼）
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "AILearn").strip(),
        "USER": os.environ.get("DB_USER", "postgres").strip(),
        "HOST": os.environ.get("DB_HOST", "localhost").strip(),
        "PORT": os.environ.get("DB_PORT", "5432").strip(),
        # 刻意不設定 PASSWORD：密碼由 libpq 依 PGPASSFILE 讀取
        "CONN_MAX_AGE": 0,
        "OPTIONS": {},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# 國際化與時區（AD-10：儲存 UTC、顯示 Asia/Taipei）
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "zh-hant"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# 靜態檔案（AD-16：正式環境由 Django 同源供應前端產物）
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

WHITE_NOISE_AUTOREFRESH = True
# base 層用最簡單的靜態檔案儲存，避免未執行 collectstatic 時就要求 manifest；
# 正式環境的 manifest 儲存由 prod.py 啟用。
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # 單一例外處理器（AD-17）：所有錯誤統一轉為 {code, detail, field_errors}
    "EXCEPTION_HANDLER": "core.handler.exception_handler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # 認證採 session（AD-6）：Django session cookie + CSRF token 是唯一機制。
    # 未認證的請求一律回 401 auth.unauthenticated、越權回 403 auth.forbidden
    # （由 core.permissions 的 permission class 丟出領域例外）。
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # 預設放行；各 view 自行宣告需要的權限（AD-5）
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# ---------------------------------------------------------------------------
# 記錄：不記錄密碼或完整憑證（AD-18）
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{asctime}] {levelname} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
