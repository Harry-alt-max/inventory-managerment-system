import { useI18n } from "../../i18n";
import type { MessageKey } from "../../i18n";
import { NAV_ITEMS } from "./nav-items";
import type { NavItem } from "./nav-items";

interface SidebarProps {
  activeKey: string;
  onSelect: (item: NavItem) => void;
}

/**
 * 左側固定導覽（DESIGN.md「側邊導覽」：選取項以 primary 左側指示條 + raised 底）。
 *
 * 斷點行為（DESIGN.md）：≥1280px 完整展開（{spacing.sidebar-width} = 232px）；
 * 1024–1279px 摺疊為圖示列（僅留 {components.圖示.size-md} = 20px 圖示）。
 */
export function Sidebar({ activeKey, onSelect }: SidebarProps) {
  const { t } = useI18n();

  const groups: Array<{ key: NavItem["group"]; labelKey: MessageKey }> = [
    { key: "workspace", labelKey: "nav.group.workspace" },
    { key: "management", labelKey: "nav.group.management" },
  ];

  return (
    <aside className="flex w-14 shrink-0 flex-col border-r border-border bg-surface xl:w-58">
      <div className="flex h-14 items-center justify-center gap-2 border-b border-border px-2 xl:justify-start xl:px-4">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-primary text-sm font-semibold text-primary-fg">
          {t("app.brandMark")}
        </span>
        <div className="hidden flex-col leading-tight xl:flex">
          <span className="text-sm font-semibold text-fg">{t("app.name")}</span>
          <span className="text-xs text-fg-muted">{t("app.subtitle")}</span>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-4 overflow-y-auto p-3">
        {groups.map((group) => (
          <div key={group.key} className="flex flex-col gap-1">
            <span className="hidden px-2 text-xs font-medium text-fg-muted xl:block">
              {t(group.labelKey)}
            </span>
            {NAV_ITEMS.filter((item) => item.group === group.key).map((item) => {
              const Icon = item.icon;
              const isActive = item.key === activeKey;
              const label = t(item.labelKey);
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => onSelect(item)}
                  title={label}
                  aria-current={isActive ? "page" : undefined}
                  aria-label={label}
                  className={`flex items-center justify-center gap-2 rounded-sm border-l-2 px-2 py-1.5 text-left text-sm transition-colors xl:justify-start ${
                    isActive
                      ? "border-l-primary bg-surface-raised font-medium text-fg"
                      : "border-l-transparent text-fg-secondary hover:bg-muted-tint"
                  }`}
                >
                  <Icon size={20} strokeWidth={1.5} aria-hidden="true" />
                  <span className="hidden xl:inline">{label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
