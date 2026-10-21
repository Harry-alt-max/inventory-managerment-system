"""core 共用檢視。"""
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class ApiNotFoundView(APIView):
    """捕捉 /api/v1/ 底下未定義的路徑。

    交由 DRF 拋出 NotFound，再由單一 exception handler（core.handler）
    轉成統一錯誤包絡，避免 Django 預設的 HTML 404。
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def initial(self, request, *args, **kwargs):
        raise NotFound()
