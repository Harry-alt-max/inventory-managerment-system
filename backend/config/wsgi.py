"""WSGI 進入點。

正式環境以 waitress 伺服此應用；前端靜態檔由 WhiteNoise 同源供應
（WhiteNoise 已掛在 MIDDLEWARE，見 config/settings/base.py）。
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
