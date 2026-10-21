import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { AppShell, NAV_ITEMS } from "./features/shell";
import type { NavItem } from "./features/shell";
import { useI18n } from "./i18n";
import { HomePage } from "./pages/HomePage";

export default function App() {
  const { t } = useI18n();
  const [activeKey, setActiveKey] = useState("dashboard");

  const activeItem: NavItem = NAV_ITEMS.find((item) => item.key === activeKey) ?? NAV_ITEMS[0];

  function handleSelect(item: NavItem) {
    setActiveKey(item.key);
  }

  return (
    <AppShell
      title={t(activeItem.labelKey)}
      description={t("app.subtitle")}
      activeKey={activeKey}
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
