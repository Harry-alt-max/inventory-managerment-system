"""API 契約測試：對應計畫 I/O & Edge-Case Matrix 的前兩列。

矩陣列：
1. 健康檢查：GET /api/v1/health → 200 {"status","version"}；DB 不可連 → 503 db.unavailable
2. 未知路徑：GET /api/v1/nope → 404 且 body 為統一錯誤包絡

契約重點（AD-7、AD-17）：所有錯誤 body 的鍵集合固定為
``{code, detail, field_errors}``，不得出現額外鍵或缺少鍵。
"""
from __future__ import annotations

from unittest import mock

import pytest
from django.db import OperationalError

from core.handler import error_response

ENVELOPE_KEYS = {"code", "detail", "field_errors"}


@pytest.mark.django_db
def test_health_returns_status_and_version(client):
    """矩陣列 1：健康檢查回 200 且含 status 與 version。"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"]


def test_health_returns_503_when_database_unavailable(client):
    """矩陣列 1：資料庫不可連時回 503 與 db.unavailable，仍是統一包絡。"""
    with mock.patch("accounts.views.connection") as fake_connection:
        fake_connection.cursor.side_effect = OperationalError("boom")
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    body = response.json()
    assert body["code"] == "db.unavailable"
    assert set(body) == ENVELOPE_KEYS


def test_unknown_api_path_returns_error_envelope(client):
    """矩陣列 2：未知路徑回 404，且 body 是統一錯誤包絡。"""
    response = client.get("/api/v1/nope")

    assert response.status_code == 404
    body = response.json()
    assert set(body) == ENVELOPE_KEYS
    assert body["code"] == "resource.not_found"


def test_error_response_shape_is_stable():
    """錯誤包絡的形狀由單一 helper 決定：鍵固定、field_errors 預設為空物件。"""
    response = error_response("resource.not_found", "Resource not found.", status=404)

    assert set(response.data) == ENVELOPE_KEYS
    assert response.data["code"] == "resource.not_found"
    assert response.data["field_errors"] == {}


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/api/v1/health", "/api/v1/nope"])
def test_api_responses_are_json(client, path):
    """API 一律回 JSON（不是 Django 的 HTML 錯誤頁）。"""
    response = client.get(path)

    assert response["Content-Type"].startswith("application/json")
