"""accounts app 的 API 檢視。"""
from __future__ import annotations

from django.db import InterfaceError, OperationalError, connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.handler import error_response
from core.version import APP_VERSION


class HealthView(APIView):
    """健康檢查：回應後端版本字串，並確認資料庫可連線。

    - 正常：200 ``{"status": "ok", "version": "..."}``
    - 資料庫不可連：503，統一錯誤包絡 ``{"code": "db.unavailable", ...}``
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except (OperationalError, InterfaceError):
            return error_response(
                "db.unavailable",
                "Database connection failed.",
                status=503,
            )

        return Response({"status": "ok", "version": APP_VERSION})
