"""權限目錄（AD-5）。

本模組是「權限的唯一宣告處」，內容分三塊：

1. **permission codename 常數** —— 與 ``accounts.User.Meta.permissions`` 一一對應。
   所有 permission 都掛在 ``accounts.user`` 這個 content type 上，codename
   一律是 ``accounts.<codename>``。
2. **角色 → 權限集合的對應** —— ``ROLE_PERMISSIONS`` 直接對應 PRD FR-2 的
   權限矩陣（倉管／採購／銷售／會計）。
3. **view 宣告所需權限用的 helper** —— ``require_permissions(...)`` 與
   ``RequireAuthenticated``（DRF permission class）。

原則（AD-5）：

- 權限以 Django auth 的 Group/Permission 落地，不另建第二套權限系統；
- **讀寫權限分離**：唯讀角色不得取得任何寫入 permission（會計只讀）；
- 越權請求在 view 層被拒絕（403），不得只靠前端隱藏按鈕。

PRD FR-2 權限矩陣對應（✔ = 允許、— = 不允許）：

| 功能模組 | 倉管 | 採購 | 銷售 | 會計 |
| --- | --- | --- | --- | --- |
| 商品與庫存查詢 | ✔ | ✔ | ✔ | ✔（唯讀） |
| 入庫／領用／移轉 | ✔ | — | — | — |
| 供應商與採購批次 | — | ✔ | — | — |
| 水位與待補貨清單 | — | ✔ | ✔（唯讀） | ✔（唯讀） |
| 銷貨單 | — | — | ✔ | 唯讀可見 |
| 調貨單 | ✔（唯讀可見，不可建立） | — | ✔ | — |
| 毛利與成本檢視 | — | — | ✔ | ✔ |
| 帳號與角色指派 | ✔ | — | — | — |

兩處需要說明的取捨：

- **會計可唯讀檢視銷貨紀錄**：FR-2 的「毛利與成本檢視 ✔（會計）」與 UJ-4
  （會計逐筆核對銷貨的折後金額、成本與毛利）都要求看得到銷貨紀錄，因此會計
  另給唯讀的 ``view_sales_order``；它拿不到任何寫入 permission（AD-5）。
- **商品主檔／倉庫位置的寫入權限不在本 story**：FR-2 矩陣只涵蓋「商品與庫存
  查詢」，FR-4（建商品主檔）與 FR-10（倉庫與位置）屬於 catalog epic，屆時
  再依 FR-4／FR-10 的敘述補上對應的寫入 permission，並更新本模組。
"""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from .exceptions import AuthenticationRequired, PermissionDenied

# ---------------------------------------------------------------------------
# 1. permission codename 常數
# ---------------------------------------------------------------------------

# 唯讀（查詢）權限
PERM_VIEW_CATALOG = "accounts.view_catalog"
PERM_VIEW_STOCK = "accounts.view_stock"
PERM_VIEW_SUPPLIER = "accounts.view_supplier"
PERM_VIEW_BATCH = "accounts.view_batch"
PERM_VIEW_REPLENISHMENT = "accounts.view_replenishment"
PERM_VIEW_SALES_ORDER = "accounts.view_sales_order"
PERM_VIEW_TRANSFER_ORDER = "accounts.view_transfer_order"
PERM_VIEW_MARGIN = "accounts.view_margin"

# 寫入權限
PERM_MANAGE_SUPPLIER = "accounts.manage_supplier"
PERM_MANAGE_BATCH = "accounts.manage_batch"
PERM_MANAGE_REPLENISHMENT = "accounts.manage_replenishment"
PERM_MANAGE_ACCOUNTS = "accounts.manage_accounts"
PERM_CREATE_STOCK_INBOUND = "accounts.create_stock_inbound"
PERM_CREATE_STOCK_ISSUE = "accounts.create_stock_issue"
PERM_CREATE_STOCK_TRANSFER = "accounts.create_stock_transfer"
PERM_CREATE_SALES_ORDER = "accounts.create_sales_order"
PERM_CREATE_TRANSFER_ORDER = "accounts.create_transfer_order"

#: 全部 permission codename（供 seed 與守門測試使用）
ALL_PERMISSIONS: tuple[str, ...] = (
    PERM_VIEW_CATALOG,
    PERM_VIEW_STOCK,
    PERM_VIEW_SUPPLIER,
    PERM_VIEW_BATCH,
    PERM_VIEW_REPLENISHMENT,
    PERM_VIEW_SALES_ORDER,
    PERM_VIEW_TRANSFER_ORDER,
    PERM_VIEW_MARGIN,
    PERM_MANAGE_SUPPLIER,
    PERM_MANAGE_BATCH,
    PERM_MANAGE_REPLENISHMENT,
    PERM_MANAGE_ACCOUNTS,
    PERM_CREATE_STOCK_INBOUND,
    PERM_CREATE_STOCK_ISSUE,
    PERM_CREATE_STOCK_TRANSFER,
    PERM_CREATE_SALES_ORDER,
    PERM_CREATE_TRANSFER_ORDER,
)

#: 寫入類 permission（唯讀角色不得取得；守門測試以此檢查讀寫分離）
WRITE_PERMISSIONS: frozenset[str] = frozenset(
    permission
    for permission in ALL_PERMISSIONS
    if not permission.startswith("accounts.view_")
)

# ---------------------------------------------------------------------------
# 2. 角色（PRD FR-2：v1 固定四種，不可自訂）
# ---------------------------------------------------------------------------

ROLE_WAREHOUSE = "warehouse"
ROLE_PURCHASING = "purchasing"
ROLE_SALES = "sales"
ROLE_ACCOUNTING = "accounting"

#: 角色代碼 → Django auth Group 名稱（群組名稱是資料，不是文案）
ROLE_GROUP_NAMES: dict[str, str] = {
    ROLE_WAREHOUSE: "倉管",
    ROLE_PURCHASING: "採購",
    ROLE_SALES: "銷售",
    ROLE_ACCOUNTING: "會計",
}

#: 角色代碼 → 權限集合（PRD FR-2 的權限矩陣）
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    # 倉管：商品與庫存查詢、入庫／領用／移轉、調貨單唯讀可見、帳號與角色指派
    ROLE_WAREHOUSE: frozenset(
        {
            PERM_VIEW_CATALOG,
            PERM_VIEW_STOCK,
            PERM_VIEW_TRANSFER_ORDER,
            PERM_CREATE_STOCK_INBOUND,
            PERM_CREATE_STOCK_ISSUE,
            PERM_CREATE_STOCK_TRANSFER,
            PERM_MANAGE_ACCOUNTS,
        }
    ),
    # 採購：商品與庫存查詢、供應商與採購批次、水位與待補貨清單（含設定）
    ROLE_PURCHASING: frozenset(
        {
            PERM_VIEW_CATALOG,
            PERM_VIEW_STOCK,
            PERM_VIEW_SUPPLIER,
            PERM_VIEW_BATCH,
            PERM_MANAGE_SUPPLIER,
            PERM_MANAGE_BATCH,
            PERM_VIEW_REPLENISHMENT,
            PERM_MANAGE_REPLENISHMENT,
        }
    ),
    # 銷售：商品與庫存查詢、銷貨單、調貨單可建立、待補貨唯讀、毛利與成本檢視
    ROLE_SALES: frozenset(
        {
            PERM_VIEW_CATALOG,
            PERM_VIEW_STOCK,
            PERM_VIEW_SALES_ORDER,
            PERM_CREATE_SALES_ORDER,
            PERM_VIEW_TRANSFER_ORDER,
            PERM_CREATE_TRANSFER_ORDER,
            PERM_VIEW_REPLENISHMENT,
            PERM_VIEW_MARGIN,
        }
    ),
    # 會計：唯讀（商品與庫存查詢、待補貨、銷貨紀錄、毛利與成本檢視）
    ROLE_ACCOUNTING: frozenset(
        {
            PERM_VIEW_CATALOG,
            PERM_VIEW_STOCK,
            PERM_VIEW_REPLENISHMENT,
            PERM_VIEW_SALES_ORDER,
            PERM_VIEW_MARGIN,
        }
    ),
}

#: 角色代碼 → Group 名稱的反向對應
_GROUP_NAME_TO_ROLE: dict[str, str] = {
    name: role for role, name in ROLE_GROUP_NAMES.items()
}


def permissions_for_role(role: str) -> frozenset[str]:
    """取得某角色的權限集合。"""
    try:
        return ROLE_PERMISSIONS[role]
    except KeyError as exc:  # pragma: no cover - 呼叫端錯誤
        raise KeyError(f"未知的角色代碼：{role}") from exc


def role_codes_for_user(user) -> list[str]:
    """取得使用者所屬的角色代碼清單（依固定角色順序，穩定輸出）。"""
    if not user or not user.is_authenticated:
        return []
    group_names = set(user.groups.values_list("name", flat=True))
    return [
        role for role in ROLE_GROUP_NAMES if ROLE_GROUP_NAMES[role] in group_names
    ]


def group_name_for_role(role: str) -> str:
    """取得某角色對應的 Django auth Group 名稱。"""
    return ROLE_GROUP_NAMES[role]


# ---------------------------------------------------------------------------
# 3. view 宣告所需權限用的 helper
# ---------------------------------------------------------------------------


class _BasePermission(BasePermission):
    """共用檢查邏輯：未登入 → 401、權限不足 → 403。"""

    def _check(self, request, required: tuple[str, ...]) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            raise AuthenticationRequired()
        if required and not user.has_perms(required):
            raise PermissionDenied()
        return True


class RequireAuthenticated(_BasePermission):
    """要求已登入；未登入回 401 ``auth.unauthenticated``。

    DRF 預設在沒有 ``WWW-Authenticate`` 標頭時會把未認證降級成 403，
    與契約（未認證一律 401）不符，因此這裡直接丟領域例外。
    """

    def has_permission(self, request, view) -> bool:
        return self._check(request, ())


def require_permissions(*permissions: str) -> type[BasePermission]:
    """建立「需要指定權限」的 permission class（AD-5）。

    用法（view 宣告所需權限）::

        class StockInboundView(APIView):
            permission_classes = [require_permissions(PERM_CREATE_STOCK_INBOUND)]

    未登入回 401 ``auth.unauthenticated``；權限不足回 403 ``auth.forbidden``。
    """

    class RequirePermissions(_BasePermission):
        def has_permission(self, request, view) -> bool:
            return self._check(request, permissions)

    RequirePermissions.__name__ = "RequirePermissions"
    RequirePermissions.__qualname__ = "RequirePermissions"
    return RequirePermissions
