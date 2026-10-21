"""專案根 URL 設定。

- ``/admin/``    Django admin
- ``/api/v1/``   REST API（前綴固定，AD-7）
- ``/api/...``   其他 API 前綴 → 同樣回統一錯誤包絡的 404
- 其餘路徑       前端單頁应用：真實檔案直接提供，其餘回 index.html

前端建置產物位於 ``frontend/dist``；正式環境可改由 WhiteNoise 供應同一份檔案。
"""
from pathlib import Path, PurePosixPath

from django.contrib import admin
from django.http import Http404, HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve

from core.views import ApiNotFoundView

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = (PROJECT_ROOT / "frontend" / "dist").resolve()


def frontend_view(request, path: str = ""):
    """提供前端建置產物（client-side routing 的 fallback）。

    - 路徑對應到 ``frontend/dist`` 下的真實檔案 → 直接提供該檔案
    - 帶副檔名但檔案不存在（``.js``／``.css`` 等）→ 404（不得以 HTML 回應資源檔）
    - 其餘路徑 → 回 ``index.html``
    """
    candidate = (FRONTEND_DIST / path.lstrip("/")).resolve()
    try:
        candidate.relative_to(FRONTEND_DIST)
    except ValueError:
        raise Http404("Invalid path.")

    if candidate.is_file():
        return serve(request, path, document_root=FRONTEND_DIST)

    if PurePosixPath(path).suffix:
        raise Http404("Asset not found.")

    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        raise Http404("前端尚未建置（frontend/dist/index.html 不存在）。")
    return HttpResponse(index.read_bytes(), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("core.urls")),
    # 其他 API 前綴（例如 /api/v2/）同樣回統一錯誤包絡的 404，不落到 SPA fallback
    re_path(r"^api/", ApiNotFoundView.as_view(), name="api-not-found"),
    re_path(r"^(?P<path>.*)$", frontend_view, name="frontend"),
]
