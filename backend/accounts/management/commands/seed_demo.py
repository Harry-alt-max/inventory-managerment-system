"""建立四種角色群組與示範帳號。

用途：在沒有帳號管理介面（FR-20）的情況下，讓系統可以立即試登入。

- 依 `core/permissions.py` 的角色 → 權限對應（PRD FR-2）建立／更新四個群組；
- 每個角色建立一個示範帳號並指派角色；
- 密碼預設**隨機產生並印出**（不寫入任何檔案，AD-15）；也可用
  ``--password`` 指定。

指令可重複執行：群組權限會重新對齊，示範帳號的密碼會重新設定並再次印出。
"""
from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.crypto import get_random_string

from accounts.models import User
from core.permissions import ROLE_GROUP_NAMES, ROLE_PERMISSIONS

#: 示範帳號帳號代號
DEMO_USERNAMES = {
    role: f"demo_{role}" for role in ROLE_GROUP_NAMES
}

#: 示範帳號顯示名稱（姓／名）
DEMO_NAMES = {
    "warehouse": ("示範", "倉管"),
    "purchasing": ("示範", "採購"),
    "sales": ("示範", "銷售"),
    "accounting": ("示範", "會計"),
}

_PASSWORD_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"


class Command(BaseCommand):
    help = "建立四種角色群組與各一個示範帳號，並印出登入資訊。"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--password",
            default=None,
            help="示範帳號共用的密碼；未指定時隨機產生並印出（不寫入檔案）。",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        explicit_password = options.get("password")

        groups = self._sync_groups()
        credentials = self._sync_demo_users(groups, explicit_password)

        self.stdout.write("角色群組已建立／更新：")
        for role, group in groups.items():
            self.stdout.write(f"  {ROLE_GROUP_NAMES[role]}：{len(group.permissions.values())} 項權限")

        self.stdout.write("")
        self.stdout.write("示範帳號（密碼僅顯示於本指令輸出）：")
        for entry in credentials:
            self.stdout.write(f"  帳號：{entry['username']}")
            self.stdout.write(f"    顯示名稱：{entry['display_name']}")
            self.stdout.write(f"    角色：{entry['role_name']}")
            self.stdout.write(f"    密碼：{entry['password']}")

    def _sync_groups(self) -> dict[str, Group]:
        """建立／更新四個角色群組，並對齊權限集合（AD-5）。"""
        permissions = self._load_permissions()
        groups: dict[str, Group] = {}
        for role, group_name in ROLE_GROUP_NAMES.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.set(permissions[role])
            groups[role] = group
        return groups

    def _load_permissions(self) -> dict[str, list[Permission]]:
        """把角色 → permission codename 對應解析成 Permission 物件。"""
        available = {
            permission.codename: permission
            for permission in Permission.objects.filter(
                content_type__app_label="accounts",
            )
        }
        resolved: dict[str, list[Permission]] = {}
        missing: list[str] = []
        for role, codenames in ROLE_PERMISSIONS.items():
            resolved[role] = []
            for codename in sorted(codenames):
                permission = available.get(codename.split(".", 1)[-1])
                if permission is None:
                    missing.append(codename)
                    continue
                resolved[role].append(permission)
        if missing:
            raise CommandError(
                "找不到下列 permission（請先執行 migrate）：" + "、".join(sorted(missing))
            )
        return resolved

    def _sync_demo_users(self, groups: dict[str, object], explicit_password) -> list[dict[str, str]]:
        """建立／更新示範帳號並指派角色，回傳可印出的登入資訊。"""
        credentials: list[dict[str, str]] = []
        for role, group in groups.items():
            username = DEMO_USERNAMES[role]
            password = explicit_password or get_random_string(12, _PASSWORD_ALPHABET)
            last_name, first_name = DEMO_NAMES[role]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                },
            )
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.set_password(password)
            user.save()
            user.groups.set([group])

            credentials.append(
                {
                    "username": username,
                    "display_name": user.get_full_name().strip() or username,
                    "role_name": ROLE_GROUP_NAMES[role],
                    "password": password,
                    "created": "建立" if created else "更新",
                }
            )
        return credentials
