import type { LucideIcon } from "lucide-react";
import { Boxes, LayoutDashboard, Package, Receipt, Settings, Users } from "lucide-react";

import type { MessageKey } from "../../i18n";

export interface NavItem {
  key: string;
  labelKey: MessageKey;
  icon: LucideIcon;
  group: "workspace" | "management";
  /** 本 story 是否已有可用的內容頁。 */
  implemented: boolean;
}

/** 側邊導覽項目（依 spine 的四個 epic 分組）。 */
export const NAV_ITEMS: NavItem[] = [
  {
    key: "dashboard",
    labelKey: "nav.dashboard",
    icon: LayoutDashboard,
    group: "workspace",
    implemented: true,
  },
  {
    key: "accounts",
    labelKey: "nav.accounts",
    icon: Users,
    group: "management",
    implemented: false,
  },
  {
    key: "catalog",
    labelKey: "nav.catalog",
    icon: Package,
    group: "management",
    implemented: false,
  },
  {
    key: "stock",
    labelKey: "nav.stock",
    icon: Boxes,
    group: "management",
    implemented: false,
  },
  {
    key: "sales",
    labelKey: "nav.sales",
    icon: Receipt,
    group: "management",
    implemented: false,
  },
  {
    key: "settings",
    labelKey: "nav.settings",
    icon: Settings,
    group: "management",
    implemented: false,
  },
];
