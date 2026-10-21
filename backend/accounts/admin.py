"""accounts app 的 Django admin 設定。"""
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group

from .models import User


class AccountsUserAdmin(UserAdmin):
    """沿用 Django 內建 UserAdmin 的行為。"""


if not admin.site.is_registered(User):
    admin.site.register(User, AccountsUserAdmin)

if not admin.site.is_registered(Group):
    admin.site.register(Group, GroupAdmin)
