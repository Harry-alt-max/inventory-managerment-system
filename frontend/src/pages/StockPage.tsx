import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import { fetchStock } from "../lib/api";
import { MovementTable } from "./InboundPage";

/** 庫存現況：商品 × 位置 × 數量（AD-29：唯一的庫存真相）。 */
export function StockPage() {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const stock = useQuery({ queryKey: ["stock", query], queryFn: () => fetchStock(query) });

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("stock.list.title")}</CardTitle>
          <CardDescription>{t("stock.list.description")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <input
            type="search"
            className="h-9 w-72 rounded-sm border border-border-strong bg-surface px-3 text-sm text-fg placeholder:text-fg-muted"
            placeholder={t("stock.list.search")}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />

          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-fg-muted">
                <th className="px-3 py-2 font-medium">{t("catalog.items.code")}</th>
                <th className="px-3 py-2 font-medium">{t("catalog.items.name")}</th>
                <th className="px-3 py-2 font-medium">{t("stock.list.warehouse")}</th>
                <th className="px-3 py-2 font-medium">{t("stock.list.location")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("stock.list.quantity")}</th>
              </tr>
            </thead>
            <tbody>
              {(stock.data ?? []).map((row) => (
                <tr key={`${row.item_code}-${row.location_code}`} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{row.item_code}</td>
                  <td className="px-3 py-2 text-fg">{row.item_name}</td>
                  <td className="px-3 py-2 text-fg-secondary">
                    {row.warehouse_code} {row.warehouse_name}
                  </td>
                  <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{row.location_code}</td>
                  <td className="px-3 py-2 text-right font-medium tabular-nums text-fg">{row.quantity}</td>
                </tr>
              ))}
              {(stock.data ?? []).length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-center text-fg-muted">
                    {t("stock.list.empty")}
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <MovementTable />
    </div>
  );
}

export default StockPage;
