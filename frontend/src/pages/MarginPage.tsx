import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import { fetchMargins } from "../lib/api";

/** 毛利查核（會計唯讀）：依日期或單號查詢每筆銷貨的折後金額、成本與毛利。 */
export function MarginPage() {
  const { t } = useI18n();
  const [orderNo, setOrderNo] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [applied, setApplied] = useState({ order_no: "", date_from: "", date_to: "" });

  const margins = useQuery({
    queryKey: ["margins", applied],
    queryFn: () => fetchMargins(applied),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("margins.title")}</CardTitle>
        <CardDescription>{t("margins.description")}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-fg-secondary">{t("margins.orderNo")}</span>
            <input
              className="h-9 w-48 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
              value={orderNo}
              onChange={(event) => setOrderNo(event.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-fg-secondary">{t("margins.from")}</span>
            <input
              type="date"
              className="h-9 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
              value={dateFrom}
              onChange={(event) => setDateFrom(event.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-fg-secondary">{t("margins.to")}</span>
            <input
              type="date"
              className="h-9 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
              value={dateTo}
              onChange={(event) => setDateTo(event.target.value)}
            />
          </label>
          <button
            type="button"
            className="h-9 rounded-sm bg-primary px-3 text-sm font-medium text-primary-fg"
            onClick={() => setApplied({ order_no: orderNo, date_from: dateFrom, date_to: dateTo })}
          >
            {t("margins.search")}
          </button>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-fg-muted">
              <th className="px-3 py-2 font-medium">{t("margins.orderNo")}</th>
              <th className="px-3 py-2 font-medium">{t("margins.time")}</th>
              <th className="px-3 py-2 font-medium">{t("margins.status")}</th>
              <th className="px-3 py-2 text-right font-medium">{t("margins.paid")}</th>
              <th className="px-3 py-2 text-right font-medium">{t("margins.cost")}</th>
              <th className="px-3 py-2 text-right font-medium">{t("margins.margin")}</th>
              <th className="px-3 py-2 font-medium">{t("margins.creator")}</th>
            </tr>
          </thead>
          <tbody>
            {(margins.data ?? []).map((order) => (
              <tr key={order.order_no} className="border-b border-border last:border-0">
                <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{order.order_no}</td>
                <td className="px-3 py-2 text-fg-secondary">
                  {new Date(order.created_at).toLocaleString("zh-TW", {
                    hour12: false,
                    timeZone: "Asia/Taipei",
                  })}
                </td>
                <td className="px-3 py-2 text-fg-secondary">{order.status_label}</td>
                <td className="px-3 py-2 text-right tabular-nums text-fg">{order.total_paid}</td>
                <td className="px-3 py-2 text-right tabular-nums text-fg">{order.total_cost}</td>
                <td className="px-3 py-2 text-right font-semibold tabular-nums text-accent-text">
                  {order.total_margin}
                </td>
                <td className="px-3 py-2 text-fg-secondary">{order.created_by}</td>
              </tr>
            ))}
            {(margins.data ?? []).length === 0 ? (
              <tr>
                <td colSpan={7} className="px-3 py-6 text-center text-fg-muted">
                  {t("margins.empty")}
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

export default MarginPage;
