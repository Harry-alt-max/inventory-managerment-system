import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut } from "lucide-react";

import { useI18n } from "../../i18n";

/** 頂列右側的使用者選單（登入功能屬於後續 story，此處為停用狀態的骨架）。 */
export function UserMenu() {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
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
        <span className="hidden lg:inline">{t("topbar.user.name")}</span>
        <ChevronDown size={16} strokeWidth={1.5} aria-hidden="true" />
      </button>

      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 w-56 rounded-lg border border-border bg-surface-raised p-2 shadow-raised"
        >
          <div className="flex flex-col gap-0.5 border-b border-border px-2 pb-2">
            <span className="text-sm font-medium text-fg">{t("topbar.user.name")}</span>
            <span className="text-xs text-fg-muted">
              {t("topbar.user.role")}: {t("common.dash")}
            </span>
          </div>
          <button
            type="button"
            role="menuitem"
            disabled
            title={t("topbar.user.signOut.disabled")}
            className="mt-1 flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm text-fg-muted disabled:cursor-not-allowed"
          >
            <LogOut size={16} strokeWidth={1.5} aria-hidden="true" />
            <span>{t("topbar.user.signOut")}</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
