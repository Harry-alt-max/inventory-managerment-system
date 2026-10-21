import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut } from "lucide-react";

import { useAuth } from "../auth";
import { useI18n } from "../../i18n";
import type { MessageKey } from "../../i18n";

/** 角色代碼 → message catalog 的顯示名稱（AD-33：文案由前端本地化）。 */
const ROLE_LABEL_KEYS: Record<string, MessageKey> = {
  warehouse: "role.warehouse",
  purchasing: "role.purchasing",
  sales: "role.sales",
  accounting: "role.accounting",
};

/** 頂列右側的使用者選單：顯示姓名與角色（唯讀），並提供登出。 */
export function UserMenu() {
  const { t } = useI18n();
  const { user, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function handlePointerDown(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [open]);

  const roleKey = user?.roles[0] ? ROLE_LABEL_KEYS[user.roles[0]] : undefined;

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await signOut();
    } finally {
      setSigningOut(false);
      setOpen(false);
    }
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t("topbar.user.menu")}
        onClick={() => setOpen((value) => !value)}
        className="flex h-9 items-center gap-2 rounded-pill border border-border-strong bg-surface px-3 text-sm text-fg hover:bg-surface-raised"
      >
        <span className="flex h-6 w-6 items-center justify-center rounded-pill bg-primary-tint text-xs font-semibold text-primary">
          {t("topbar.user.avatar")}
        </span>
        <span className="hidden lg:inline">{user?.display_name ?? t("topbar.user.name")}</span>
        <ChevronDown size={16} strokeWidth={1.5} aria-hidden="true" />
      </button>

      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 w-56 rounded-lg border border-border bg-surface-raised p-2 shadow-raised"
        >
          <div className="flex flex-col gap-0.5 border-b border-border px-2 pb-2">
            <span className="text-sm font-medium text-fg">
              {user?.display_name ?? t("topbar.user.name")}
            </span>
            <span className="text-xs text-fg-muted">
              {t("topbar.user.role")}: {roleKey ? t(roleKey) : t("role.none")}
            </span>
          </div>
          <button
            type="button"
            role="menuitem"
            onClick={() => void handleSignOut()}
            disabled={signingOut}
            className="mt-1 flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm text-fg-secondary hover:bg-muted-tint disabled:cursor-not-allowed"
          >
            <LogOut size={16} strokeWidth={1.5} aria-hidden="true" />
            <span>{signingOut ? t("topbar.user.signingOut") : t("topbar.user.signOut")}</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
