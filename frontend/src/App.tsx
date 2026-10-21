import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { useAuth } from "./features/auth";
import { AppShell, NAV_ITEMS } from "./features/shell";
import type { NavItem } from "./features/shell";
import { useI18n } from "./i18n";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  const { t } = useI18n();
  const { user, status } = useAuth();
  const [activeKey, setActiveKey] = useState("dashboard");

  // 未登入時顯示登入頁；載入中先留白避免閃爍。
  if (status === "loading") {
    return <div className="min-h-screen bg-background" />;
  }
  if (!user) {
    return <LoginPage />;
  }

  // 側邊導覽依角色顯示（EXPERIENCE.md：無權限的項目不顯示）。
  const role = user.roles[0];
  const items = NAV_ITEMS.filter((item) => item.roles.includes(role));
  const activeItem: NavItem = items.find((item) => item.key === activeKey) ?? items[0];

  function handleSelect(item: NavItem) {
    setActiveKey(item.key);
  }

  return (
    <AppShell
      title={t(activeItem.labelKey)}
      description={t("app.subtitle")}
      activeKey={activeItem.key}
      onSelectNav={handleSelect}
    >
      {activeItem.implemented ? (
        <HomePage />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>{t("nav.placeholder.title")}</CardTitle>
            <CardDescription>{t("nav.placeholder.description")}</CardDescription>
          </CardHeader>
          <CardContent>
            <span className="text-sm text-fg-secondary">{t(activeItem.labelKey)}</span>
          </CardContent>
        </Card>
      )}
    </AppShell>
  );
}
