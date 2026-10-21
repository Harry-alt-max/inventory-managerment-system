/**
 * 訊息目錄（AD-33）。
 *
 * 介面上所有使用者可見的字串都必須來自此目錄，元件內不得硬寫字。
 * zh-TW 為預設語系、en-US 為次要語系；缺少翻譯時 fallback 到 zh-TW。
 *
 * 後端只回傳機器可讀的 `code`（AD-7、AD-17），錯誤文案以 `error.<code>` 命名。
 */

export const LOCALES = ["zh-TW", "en-US"] as const;

export type Locale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "zh-TW";

const zhTW = {
  "app.name": "庫存管理系統",
  "app.subtitle": "內部進銷存後台",
  "app.brandMark": "庫",

  "nav.group.workspace": "工作區",
  "nav.group.management": "管理",
  "nav.dashboard": "總覽",
  "nav.accounts": "帳號與角色",
  "nav.catalog": "商品主檔",
  "nav.stock": "庫存",
  "nav.sales": "銷貨",
  "nav.settings": "設定",
  "nav.placeholder.title": "尚未實作",
  "nav.placeholder.description": "此模組將於後續 epic 實作，目前僅保留外框與導覽位置。",

  "topbar.search.label": "全域搜尋",
  "topbar.search.placeholder": "搜尋商品編號或名稱",
  "topbar.language": "語系",
  "topbar.theme": "色彩模式",
  "topbar.theme.light": "淺色",
  "topbar.theme.dark": "深色",
  "topbar.user.menu": "使用者選單",
  "topbar.user.name": "使用者",
  "topbar.user.role": "角色",
  "topbar.user.avatar": "U",
  "topbar.user.signOut": "登出",
  "topbar.user.signOut.disabled": "登入功能尚未實作",
  "topbar.user.signingOut": "登出中…",

  "auth.title": "登入庫存管理系統",
  "auth.description": "以公司帳號登入後台。",
  "auth.username": "帳號",
  "auth.username.placeholder": "請輸入帳號",
  "auth.password": "密碼",
  "auth.password.placeholder": "請輸入密碼",
  "auth.submit": "登入",
  "auth.submitting": "登入中…",
  "auth.hint": "連續 5 次輸入錯誤，帳號會被鎖定 15 分鐘。",

  "role.warehouse": "倉管",
  "role.purchasing": "採購",
  "role.sales": "銷售",
  "role.accounting": "會計",
  "role.none": "未指派角色",

  "home.title": "總覽",
  "home.description": "後端、資料庫與前端的連線狀態。",
  "home.card.status": "後端狀態",
  "home.card.version": "後端版本",
  "home.status.ok": "連線正常",
  "home.status.checking": "檢查中…",
  "home.status.unavailable": "後端無法連線",
  "home.status.retry": "重新檢查",
  "home.hint": "請先啟動後端（python manage.py runserver），再按「重新檢查」。",

  "health.status.label": "狀態",
  "health.version.label": "版本",

  "error.title": "發生錯誤",
  "error.code": "錯誤代碼",
  "error.unknown": "發生未預期的錯誤，請稍後再試。",
  "error.network.unreachable": "無法連線到後端服務，請確認後端是否已啟動。",
  "error.db.unavailable": "資料庫目前無法連線，請確認 PostgreSQL 與憑證設定。",
  "error.request.invalid": "請求資料有誤，請確認後重新送出。",
  "error.request.method_not_allowed": "此路徑不支援這個操作方法。",
  "error.request.not_acceptable": "請求格式無法被處理。",
  "error.request.unsupported_media_type": "不支援此種請求內容格式。",
  "error.request.throttled": "請求過於頻繁，請稍後再試。",
  "error.auth.unauthenticated": "尚未登入或登入已失效。",
  "error.auth.forbidden": "沒有權限執行此操作。",
  "error.auth.invalid_credentials": "帳號或密碼錯誤。",
  "error.auth.locked": "帳號因連續輸入錯誤已鎖定，請稍後再試。",
  "error.auth.csrf_failed": "安全驗證已失效，請重新整理頁面後再試。",
  "error.resource.not_found": "找不到指定的資源。",
  "error.resource.conflict": "資料狀態衝突，請重新整理後再試。",
  "error.resource.duplicate": "資料已存在，請改用其他值。",
  "error.stock.insufficient": "庫存不足，無法完成此操作。",
  "error.system.internal_error": "伺服器發生未預期的錯誤。",
  "error.service.unavailable": "服務暫時無法使用，請稍後再試。",

  "common.loading": "載入中…",
  "common.retry": "重試",
  "common.close": "關閉",
  "common.dash": "—",
} as const;

export type MessageKey = keyof typeof zhTW;

const enUS: Record<MessageKey, string> = {
  "app.name": "Inventory Management System",
  "app.subtitle": "Internal stock and sales back office",
  "app.brandMark": "IM",

  "nav.group.workspace": "Workspace",
  "nav.group.management": "Management",
  "nav.dashboard": "Overview",
  "nav.accounts": "Accounts & roles",
  "nav.catalog": "Item master",
  "nav.stock": "Stock",
  "nav.sales": "Sales",
  "nav.settings": "Settings",
  "nav.placeholder.title": "Not implemented yet",
  "nav.placeholder.description":
    "This module is planned for a later epic; only the shell and navigation slot exist for now.",

  "topbar.search.label": "Global search",
  "topbar.search.placeholder": "Search by item code or name",
  "topbar.language": "Language",
  "topbar.theme": "Color mode",
  "topbar.theme.light": "Light",
  "topbar.theme.dark": "Dark",
  "topbar.user.menu": "User menu",
  "topbar.user.name": "User",
  "topbar.user.role": "Role",
  "topbar.user.avatar": "U",
  "topbar.user.signOut": "Sign out",
  "topbar.user.signOut.disabled": "Sign-in is not implemented yet",
  "topbar.user.signingOut": "Signing out…",

  "auth.title": "Sign in to Inventory Management",
  "auth.description": "Sign in with your company account.",
  "auth.username": "Username",
  "auth.username.placeholder": "Enter your username",
  "auth.password": "Password",
  "auth.password.placeholder": "Enter your password",
  "auth.submit": "Sign in",
  "auth.submitting": "Signing in…",
  "auth.hint": "5 failed attempts will lock the account for 15 minutes.",

  "role.warehouse": "Warehouse",
  "role.purchasing": "Purchasing",
  "role.sales": "Sales",
  "role.accounting": "Accounting",
  "role.none": "No role assigned",

  "home.title": "Overview",
  "home.description": "Connection status across backend, database and frontend.",
  "home.card.status": "Backend status",
  "home.card.version": "Backend version",
  "home.status.ok": "Connected",
  "home.status.checking": "Checking…",
  "home.status.unavailable": "Backend unreachable",
  "home.status.retry": "Re-check",
  "home.hint": "Start the backend (python manage.py runserver), then press “Re-check”.",

  "health.status.label": "Status",
  "health.version.label": "Version",

  "error.title": "Something went wrong",
  "error.code": "Error code",
  "error.unknown": "An unexpected error occurred. Please try again later.",
  "error.network.unreachable": "Cannot reach the backend service. Please check that it is running.",
  "error.db.unavailable": "The database is currently unreachable. Please check PostgreSQL and credentials.",
  "error.request.invalid": "The request data is invalid. Please review and try again.",
  "error.request.method_not_allowed": "This operation is not allowed on this path.",
  "error.request.not_acceptable": "The request format cannot be processed.",
  "error.request.unsupported_media_type": "This request content type is not supported.",
  "error.request.throttled": "Too many requests. Please try again later.",
  "error.auth.unauthenticated": "You are not signed in, or the session has expired.",
  "error.auth.forbidden": "You do not have permission for this action.",
  "error.auth.invalid_credentials": "Incorrect username or password.",
  "error.auth.locked": "This account is locked after repeated failed attempts. Try again later.",
  "error.auth.csrf_failed": "The security check expired. Reload the page and try again.",
  "error.resource.not_found": "The requested resource was not found.",
  "error.resource.conflict": "The resource state conflicts. Please reload and try again.",
  "error.resource.duplicate": "The record already exists. Please use a different value.",
  "error.stock.insufficient": "There is not enough stock to complete this operation.",
  "error.system.internal_error": "The server hit an unexpected error.",
  "error.service.unavailable": "The service is temporarily unavailable. Please try again later.",

  "common.loading": "Loading…",
  "common.retry": "Retry",
  "common.close": "Close",
  "common.dash": "—",
};

export const catalog: Record<Locale, Record<MessageKey, string>> = {
  "zh-TW": zhTW,
  "en-US": enUS,
};

export const LOCALE_LABELS: Record<Locale, string> = {
  "zh-TW": "繁體中文",
  "en-US": "English",
};
