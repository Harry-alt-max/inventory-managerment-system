import type { LucideIcon } from "lucide-react";
import { Boxes, Calculator, LayoutDashboard, Package, PackagePlus, Receipt, Settings, Users } from "lucide-react";

import type { MessageKey } from "../../i18n";

export interface NavItem {
  key: string;
  labelKey: MessageKey;
  icon: LucideIcon;
  group: "workspace" | "management";
  /** 本 story 是否已有可用的內容頁。 */
  implemented: boolean;
  /** 可看見此項目的角色代碼（AD-5：無權限的項目不顯示）。 */
  roles: string[];
}

/** 側邊導覽項目（依 spine 的四個 epic 分組，權限依 PRD FR-2 的角色矩陣）。 */
export const NAV_ITEMS: NavItem[] = [
  {
    key: "dashboard",
    labelKey: "nav.dashboard",
    icon: LayoutDashboard,
    group: "workspace",
    implemented: true,
    roles: ["warehouse", "purchasing", "sales", "accounting"],
  },
  {
    key: "accounts",
    labelKey: "nav.accounts",
    icon: Users,
    group: "management",
    implemented: false,
    roles: ["warehouse"],
  },
  {
    key: "catalog",
    labelKey: "nav.catalog",
    icon: Package,
    group: "management",
    implemented: true,
    roles: ["warehouse", "purchasing"],
  },
  {
    key: "inbound",
    labelKey: "nav.inbound",
    icon: PackagePlus,
    group: "management",
    implemented: true,
    roles: ["warehouse"],
  },
  {
    key: "stock",
    labelKey: "nav.stock",
    icon: Boxes,
    group: "management",
    implemented: true,
    roles: ["warehouse"],
  },
  {
    key: "sales",
    labelKey: "nav.sales",
    icon: Receipt,
    group: "management",
    implemented: true,
    roles: ["sales"],
  },
  {
    key: "margins",
    labelKey: "nav.margins",
    icon: Calculator,
    group: "management",
    implemented: true,
    roles: ["sales", "accounting"],
  },
  {
    key: "settings",
    labelKey: "nav.settings",
    icon: Settings,
    group: "management",
    implemented: false,
    roles: ["warehouse", "purchasing", "sales", "accounting"],
  },
];
