"""帳號與角色模型。

依 AD-5：權限以 Django auth + Group/Permission 落地，不另建第二套權限系統。
因此使用者自訂 Django 的 ``AbstractUser``（作為 ``AUTH_USER_MODEL``），
群組（角色）沿用 Django auth 的 ``Group``。
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AuthGroup


class User(AbstractUser):
    """系統使用者。密碼一律以 Django 預設雜湊器儲存（AD-6）。

    `AUTH_USER_MODEL` 指向本模型（accounts.User），但資料表沿用 Django auth
    慣例的 `auth_user`，以便 `AILearn` 中的 auth 資料表與慣例一致。
    """

    class Meta:
        db_table = "auth_user"
        verbose_name = "使用者"
        verbose_name_plural = "使用者"


class Group(AuthGroup):
    """群組（角色）。

    為 Django auth.Group 的代理模型，讓 accounts app 成為角色設定的入口；
    實際資料表仍為 auth_group，權限來源仍是 auth.Permission。
    """

    class Meta:
        proxy = True
        verbose_name = "群組"
        verbose_name_plural = "群組"
