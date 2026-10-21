"""認證與權限的 API 測試（AD-5、AD-6、AD-17、AD-19）。

覆蓋情境：

1. 登入成功 → 200，回傳使用者身分與角色
2. 密碼錯誤 → 401 ``auth.invalid_credentials``
3. 未認證存取 → 401 ``auth.unauthenticated``
4. 登出後再存取 → 401
5. 角色缺少某項權限 → 403 ``auth.forbidden``
6. 以上每一種錯誤的 body 都是 ``{code, detail, field_errors}``
7. 登入必須帶 CSRF token（AD-6）
8. 連續失敗 5 次鎖定（AD-19）
9. 角色 → 權限對應與 PRD FR-2 一致（seed_demo 建立的群組權限）

測試使用獨立測試資料庫（config.settings.test），不會連到 `AILearn`（AD-14）。
"""
from __future__ import annotations

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from rest_framework.views import APIView

from accounts.models import User
from core.permissions import (
    PERM_MANAGE_ACCOUNTS,
    ROLE_ACCOUNTING,
    ROLE_GROUP_NAMES,
    ROLE_PERMISSIONS,
    ROLE_SALES,
    ROLE_WAREHOUSE,
    require_permissions,
)

ENVELOPE_KEYS = {"code", "detail", "field_errors"}

#: 測試專用密碼（非任何環境的真實憑證；測試資料庫與測試行程使用）
TEST_PASSWORD = "test-only-passphrase"


@pytest.fixture
def api_client() -> APIClient:
    """送出 JSON 的 API client（後端只接受 JSON parser）。"""
    return APIClient()


def _role_group(role: str) -> Group:
    """建立（或取得）某角色的群組，並對齊 `core.permissions` 的權限集合。"""
    group, _ = Group.objects.get_or_create(name=ROLE_GROUP_NAMES[role])
    codenames = [codename.split(".", 1)[-1] for codename in ROLE_PERMISSIONS[role]]
    permissions = Permission.objects.filter(
        content_type__app_label="accounts",
        codename__in=codenames,
    )
    group.permissions.set(permissions)
    return group


def _make_user(username: str, role: str) -> User:
    user = User.objects.create_user(
        username=username,
        password=TEST_PASSWORD,
        first_name="測試",
        last_name=ROLE_GROUP_NAMES[role],
    )
    user.groups.add(_role_group(role))
    return user


@pytest.fixture
def warehouse_user() -> User:
    return _make_user("warehouse_tester", ROLE_WAREHOUSE)


@pytest.fixture
def accounting_user() -> User:
    return _make_user("accounting_tester", ROLE_ACCOUNTING)


class _GuardedView(APIView):
    """測試用：宣告需要 ``manage_accounts`` 權限的檢視（AD-5）。"""

    permission_classes = [require_permissions(PERM_MANAGE_ACCOUNTS)]

    def get(self, request):
        return Response({"ok": True})


# ---------------------------------------------------------------------------
# 1. 登入成功
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_success_returns_user_and_role(api_client, warehouse_user):
    response = api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == warehouse_user.username
    assert body["user"]["roles"] == [ROLE_WAREHOUSE]
    assert body["user"]["id"] == warehouse_user.pk


# ---------------------------------------------------------------------------
# 2. 密碼錯誤 / 帳號不存在
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_with_wrong_password_returns_401(api_client, warehouse_user):
    response = api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": "wrong-passphrase"},
        format="json",
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "auth.invalid_credentials"
    assert set(body) == ENVELOPE_KEYS


@pytest.mark.django_db
def test_login_with_unknown_account_returns_same_code(api_client):
    """帳號不存在與密碼錯誤回應同一個 code（不透露帳號是否存在，AD-19）。"""
    response = api_client.post(
        "/api/v1/auth/login",
        {"username": "nobody", "password": "whatever"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["code"] == "auth.invalid_credentials"


@pytest.mark.django_db
def test_login_without_fields_returns_400_with_field_errors(api_client):
    response = api_client.post("/api/v1/auth/login", {}, format="json")

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "request.invalid"
    assert set(body["field_errors"]) == {"username", "password"}
    assert set(body) == ENVELOPE_KEYS


# ---------------------------------------------------------------------------
# 3. 未認證
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_me_without_session_returns_401(api_client):
    response = api_client.get("/api/v1/auth/me")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "auth.unauthenticated"
    assert set(body) == ENVELOPE_KEYS


@pytest.mark.django_db
def test_me_with_session_returns_user(api_client, warehouse_user):
    api_client.force_login(warehouse_user)

    response = api_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["user"]["roles"] == [ROLE_WAREHOUSE]


# ---------------------------------------------------------------------------
# 4. 登出
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_logout_ends_session(api_client, warehouse_user):
    api_client.force_login(warehouse_user)
    assert api_client.get("/api/v1/auth/me").status_code == 200

    logout_response = api_client.post("/api/v1/auth/logout", {}, format="json")
    assert logout_response.status_code == 200

    after = api_client.get("/api/v1/auth/me")
    assert after.status_code == 401
    assert after.json()["code"] == "auth.unauthenticated"


# ---------------------------------------------------------------------------
# 5. 權限不足 → 403
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_role_without_permission_returns_403(accounting_user):
    """會計角色沒有 ``manage_accounts`` → 403 ``auth.forbidden``。"""
    factory = APIRequestFactory()
    request = factory.get("/api/v1/_test/guarded")
    force_authenticate(request, user=accounting_user)

    response = _GuardedView.as_view()(request)

    assert response.status_code == 403
    body = response.data
    assert body["code"] == "auth.forbidden"
    assert set(body) == ENVELOPE_KEYS


@pytest.mark.django_db
def test_role_with_permission_is_allowed(warehouse_user):
    """倉管角色具備 ``manage_accounts`` → 允許。"""
    factory = APIRequestFactory()
    request = factory.get("/api/v1/_test/guarded")
    force_authenticate(request, user=warehouse_user)

    response = _GuardedView.as_view()(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_guard_returns_401():
    """未認證時守衛回 401（不是 403）。"""
    factory = APIRequestFactory()
    request = factory.get("/api/v1/_test/guarded")

    response = _GuardedView.as_view()(request)

    assert response.status_code == 401
    assert response.data["code"] == "auth.unauthenticated"


# ---------------------------------------------------------------------------
# 6. CSRF（AD-6）
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_requires_csrf_token(warehouse_user):
    """沒有 CSRF token 的登入請求必須被拒絕。"""
    client = APIClient(enforce_csrf_checks=True)

    response = client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": TEST_PASSWORD},
        format="json",
    )

    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "auth.csrf_failed"
    assert set(body) == ENVELOPE_KEYS


@pytest.mark.django_db
def test_login_with_csrf_token_succeeds(warehouse_user):
    """帶上 CSRF token 的登入請求可通過。"""
    client = APIClient(enforce_csrf_checks=True)
    token = client.get("/api/v1/auth/csrf").json()["csrf_token"]

    response = client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": TEST_PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 7. 帳號鎖定（AD-19）
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_account_is_locked_after_five_failures(api_client, warehouse_user):
    for _ in range(4):
        response = api_client.post(
            "/api/v1/auth/login",
            {"username": warehouse_user.username, "password": "wrong-passphrase"},
            format="json",
        )
        assert response.status_code == 401
        assert response.json()["code"] == "auth.invalid_credentials"

    # 第 5 次失敗即鎖定
    locked = api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": "wrong-passphrase"},
        format="json",
    )
    assert locked.status_code == 423
    assert locked.json()["code"] == "auth.locked"

    # 鎖定期間即使密碼正確也拒絕登入
    still_locked = api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": TEST_PASSWORD},
        format="json",
    )
    assert still_locked.status_code == 423
    assert still_locked.json()["code"] == "auth.locked"


@pytest.mark.django_db
def test_successful_login_resets_failure_counter(api_client, warehouse_user):
    api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": "wrong-passphrase"},
        format="json",
    )
    warehouse_user.refresh_from_db()
    assert warehouse_user.failed_login_count == 1

    api_client.post(
        "/api/v1/auth/login",
        {"username": warehouse_user.username, "password": TEST_PASSWORD},
        format="json",
    )
    warehouse_user.refresh_from_db()
    assert warehouse_user.failed_login_count == 0
    assert warehouse_user.locked_until is None


# ---------------------------------------------------------------------------
# 8. 權限目錄與 seed_demo（AD-5、PRD FR-2）
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_seed_demo_creates_groups_with_mapped_permissions():
    call_command("seed_demo", "--password", TEST_PASSWORD, verbosity=0)

    for role, codenames in ROLE_PERMISSIONS.items():
        group = Group.objects.get(name=ROLE_GROUP_NAMES[role])
        actual = {
            f"accounts.{permission.codename}" for permission in group.permissions.all()
        }
        assert actual == set(codenames), f"{role} 的權限與 PRD FR-2 不符"


@pytest.mark.django_db
def test_seed_demo_creates_one_account_per_role():
    call_command("seed_demo", "--password", TEST_PASSWORD, verbosity=0)

    for role in ROLE_PERMISSIONS:
        username = f"demo_{role}"
        user = User.objects.get(username=username)
        assert user.is_active
        assert user.check_password(TEST_PASSWORD)
        assert ROLE_GROUP_NAMES[role] in user.groups.values_list("name", flat=True)


@pytest.mark.django_db
def test_accounting_role_has_no_write_permission():
    """AD-5：唯讀角色不得取得任何寫入 permission。"""
    from core.permissions import WRITE_PERMISSIONS

    assert not (ROLE_PERMISSIONS[ROLE_ACCOUNTING] & WRITE_PERMISSIONS)
    assert not (ROLE_PERMISSIONS[ROLE_SALES] & {"accounts.manage_accounts"})
    assert ROLE_PERMISSIONS[ROLE_WAREHOUSE] & {"accounts.manage_accounts"}

