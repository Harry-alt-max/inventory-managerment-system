import { useState } from "react";

import { useAuth } from "../features/auth";
import { useI18n } from "../i18n";
import { ApiError } from "../lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

interface RoleOption {
  role: string;
  titleKey: "rolepicker.warehouse" | "rolepicker.purchasing" | "rolepicker.sales" | "rolepicker.accounting";
  descriptionKey:
    | "rolepicker.warehouse.description"
    | "rolepicker.purchasing.description"
    | "rolepicker.sales.description"
    | "rolepicker.accounting.description";
}

const ROLES: RoleOption[] = [
  { role: "warehouse", titleKey: "rolepicker.warehouse", descriptionKey: "rolepicker.warehouse.description" },
  { role: "purchasing", titleKey: "rolepicker.purchasing", descriptionKey: "rolepicker.purchasing.description" },
  { role: "sales", titleKey: "rolepicker.sales", descriptionKey: "rolepicker.sales.description" },
  { role: "accounting", titleKey: "rolepicker.accounting", descriptionKey: "rolepicker.accounting.description" },
];

/** 職能選擇：點一張卡直接進入（示範模式，不需要帳號密碼）。 */
export function RolePickerPage() {
  const { t, tError } = useI18n();
  const { signInAsRole } = useAuth();
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);

  async function enter(role: string) {
    setPending(role);
    setError(undefined);
    try {
      await signInAsRole(role);
    } catch (err) {
      setError(err instanceof ApiError ? tError(err.code) : t("error.unknown"));
    } finally {
      setPending(null);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <div className="flex w-full max-w-3xl flex-col gap-6">
        <div className="flex flex-col gap-1 text-center">
          <h1 className="text-2xl font-semibold text-fg">{t("rolepicker.title")}</h1>
          <p className="text-sm text-fg-secondary">{t("rolepicker.description")}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {ROLES.map((option) => (
            <Card
              key={option.role}
              className="cursor-pointer transition-colors hover:border-primary"
              role="button"
              tabIndex={0}
              onClick={() => void enter(option.role)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  void enter(option.role);
                }
              }}
            >
              <CardHeader>
                <CardTitle>{t(option.titleKey)}</CardTitle>
                <CardDescription>{t(option.descriptionKey)}</CardDescription>
              </CardHeader>
              <CardContent>
                <span className="text-sm font-medium text-primary">
                  {pending === option.role ? t("rolepicker.entering") : t("rolepicker.enter")}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>

        {error ? <p className="text-center text-sm text-danger">{error}</p> : null}

        <p className="text-center text-xs text-fg-muted">{t("rolepicker.hint")}</p>
      </div>
    </div>
  );
}

export default RolePickerPage;
