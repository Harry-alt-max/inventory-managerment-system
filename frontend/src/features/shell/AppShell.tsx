import type { ReactNode } from "react";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import type { NavItem } from "./nav-items";

interface AppShellProps {
  title: string;
  description?: string;
  activeKey: string;
  onSelectNav: (item: NavItem) => void;
  children: ReactNode;
}

/** 應用外框：左側固定導覽 + 右側主區（主區上方為頂列）。 */
export function AppShell({ title, description, activeKey, onSelectNav, children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar activeKey={activeKey} onSelect={onSelectNav} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={title} description={description} />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
