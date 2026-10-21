"""帳號與角色模型。

依 AD-5：權限以 Django auth + Group/Permission 落地，不另建第二套權限系統。
因此使用者自訂 Django 的 ``AbstractUser``（作為 ``AUTH_USER_MODEL``），
群組（角色）沿用 Django auth 的 ``Group``。

``User.Meta.permissions`` 宣告的 permission 就是 `core/permissions.py` 裡的
permission codename（AD-5：權限目錄集中於 core，實際宣告掛在 accounts 的模型上）。
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AuthGroup
from django.db import models


class User(AbstractUser):
    """系統使用者。密碼一律以 Django 預設雜湊器儲存（AD-6）。

    `AUTH_USER_MODEL` 指向本模型（accounts.User），但資料表沿用 Django auth
    慣例的 `auth_user`，以便 `AILearn` 中的 auth 資料表與慣例一致。

    連續登入失敗次數與鎖定時間存在使用者資料表上（AD-19：計數必須在 DB，
    不得放記憶體或快取）。
    """

    #: 連續登入失敗次數；達到門檻即鎖定
    failed_login_count = models.PositiveIntegerField(
        default=0,
        verbose_name="連續登入失敗次數",
    )
    #: 鎖定到期時間（UTC）；null 表示未鎖定
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="鎖定至",
    )

    class Meta:
        db_table = "auth_user"
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
        # AD-5：權限目錄（codename 與 `core/permissions.py` 一一對應）
        permissions = [
            # 唯讀
            ("view_catalog", "商品與庫存查詢"),
            ("view_stock", "庫存現況與異動紀錄查詢"),
            ("view_supplier", "供應商查詢"),
            ("view_batch", "採購批次查詢"),
            ("view_replenishment", "水位與待補貨清單查詢"),
            ("view_sales_order", "銷貨單與銷貨紀錄查詢"),
            ("view_transfer_order", "調貨單查詢"),
            ("view_margin", "毛利與成本檢視"),
            # 寫入
            ("manage_supplier", "供應商維護"),
            ("manage_batch", "採購批次建立"),
            ("manage_item", "商品主檔維護"),
            ("manage_warehouse", "倉庫與庫存位置維護"),
            ("manage_replenishment", "水位設定"),
            ("manage_accounts", "帳號與角色指派"),
            ("create_stock_inbound", "入庫作業"),
            ("create_stock_issue", "領用作業"),
            ("create_stock_transfer", "同倉移轉作業"),
            ("create_sales_order", "銷貨單建立"),
            ("create_transfer_order", "調貨單建立"),
        ]


class Group(AuthGroup):
    """群組（角色）。

    為 Django auth.Group 的代理模型，讓 accounts app 成為角色設定的入口；
    實際資料表仍為 auth_group，權限來源仍是 auth.Permission。
    """

    class Meta:
        proxy = True
        verbose_name = "群組"
        verbose_name_plural = "群組"
