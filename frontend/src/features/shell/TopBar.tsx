import { Moon, Search, Sun } from "lucide-react";

import { useI18n } from "../../i18n";
import { useTheme } from "../../lib/theme";
import { UserMenu } from "./UserMenu";

interface TopBarProps {
  title: string;
  description?: string;
}

/**
 * 頂列（DESIGN.md「頂列」）：左：頁面標題；中：全域搜尋；右：色彩模式、使用者選單。
 *
 * v1 介面只出繁體中文（AD-33），語系切換已停用（catalog 的 en-US 條目保留待補）。
 */
export function TopBar({ title, description }: TopBarProps) {
  const { t } = useI18n();
  const { mode, toggle } = useTheme();

  return (
    <header className="flex h-14 shrink-0 items-center gap-6 border-b border-border bg-surface px-6">
      <div className="flex min-w-0 flex-col leading-tight">
        <h1 className="truncate text-xl font-semibold text-fg">{title}</h1>
        {description ? <span className="truncate text-xs text-fg-muted">{description}</span> : null}
      </div>

      <div className="relative ml-auto hidden w-72 md:block">
        <Search
          size={16}
          strokeWidth={1.5}
          aria-hidden="true"
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-fg-muted"
        />
        <input
          type="search"
          aria-label={t("topbar.search.label")}
          placeholder={t("topbar.search.placeholder")}
          className="h-9 w-full rounded-sm border border-border-strong bg-surface pl-9 pr-3 text-sm text-fg placeholder:text-fg-muted"
        />
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggle}
          aria-label={t("topbar.theme")}
          title={mode === "light" ? t("topbar.theme.dark") : t("topbar.theme.light")}
          className="flex h-9 w-9 items-center justify-center rounded-pill border border-border-strong bg-surface text-fg-secondary hover:bg-surface-raised"
        >
          {mode === "light" ? (
            <Moon size={16} strokeWidth={1.5} aria-hidden="true" />
          ) : (
            <Sun size={16} strokeWidth={1.5} aria-hidden="true" />
          )}
        </button>

        <UserMenu />
      </div>
    </header>
  );
}
