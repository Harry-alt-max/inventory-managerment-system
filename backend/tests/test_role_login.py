"""以角色直接進入的示範模式（``POST /api/v1/auth/login-as``）。

角色選擇取代帳號密碼輸入：選一個職能即以該職能的示範帳號建立 session，
權限仍由 Django auth 的群組權限決定（AD-5）。此模式**僅開發環境可用**。
"""
from __future__ import annotations

import pytest
from django.test import override_settings

from accounts.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_accounts() -> dict[str, User]:
    """建立四個角色的示範帳號（測試庫是獨立的，沒有 seed 產生的帳號）。"""
    from django.contrib.auth.models import Group

    from accounts.management.commands.seed_demo import DEMO_USERNAMES
    from core.permissions import ROLE_GROUP_NAMES

    accounts = {}
    for role, username in DEMO_USERNAMES.items():
        user = User.objects.create_user(username=username, password="pw-for-test-1234")
        group, _ = Group.objects.get_or_create(name=ROLE_GROUP_NAMES[role])
        user.groups.set([group])
        accounts[role] = user
    return accounts


@override_settings(DEMO_ROLE_LOGIN=True)
def test_role_login_creates_session(client, demo_accounts):
    """選一個角色即可進入，並帶回該角色。"""
    response = client.post(
        "/api/v1/auth/login-as", {"role": "warehouse"}, content_type="application/json"
    )

    assert response.status_code == 200, response.content
    assert response.json()["user"]["roles"] == ["warehouse"]

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["roles"] == ["warehouse"]


@override_settings(DEMO_ROLE_LOGIN=True)
def test_role_login_rejects_unknown_role(client):
    """未知角色回 400 並指出欄位。"""
    response = client.post(
        "/api/v1/auth/login-as", {"role": "boss"}, content_type="application/json"
    )

    assert response.status_code == 400
    assert "role" in response.json()["field_errors"]


def test_role_login_is_disabled_by_default(client):
    """正式環境（未開啟 DEMO_ROLE_LOGIN）一律拒絕角色登入。"""
    response = client.post(
        "/api/v1/auth/login-as", {"role": "warehouse"}, content_type="application/json"
    )

    assert response.status_code == 403
    assert response.json()["code"] == "auth.forbidden"


@override_settings(DEMO_ROLE_LOGIN=True)
def test_role_login_uses_the_demo_account_of_that_role(client, demo_accounts):
    """登入後的身分就是該角色的示範帳號。"""
    response = client.post(
        "/api/v1/auth/login-as", {"role": "accounting"}, content_type="application/json"
    )

    assert response.status_code == 200
    username = response.json()["user"]["username"]
    assert username == "demo_accounting"
    assert User.objects.get(username=username).is_active
