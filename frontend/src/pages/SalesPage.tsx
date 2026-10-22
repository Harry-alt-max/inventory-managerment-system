import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import {
  ApiError,
  createSalesOrder,
  fetchItems,
  fetchStock,
  quoteOrder,
  submitSalesOrder,
} from "../lib/api";
import type { QuoteResult } from "../lib/api";

interface DraftLine {
  item_code: string;
  location_code: string;
  quantity: number;
  unit_price: string;
}

/** 開單：組多商品銷貨單 → 試算毛利 → 建立並送出。 */
export function SalesPage() {
  const { t, tError } = useI18n();
  const queryClient = useQueryClient();

  const stock = useQuery({ queryKey: ["stock"], queryFn: () => fetchStock() });
  const catalog = useQuery({ queryKey: ["items"], queryFn: () => fetchItems() });
  const [lines, setLines] = useState<DraftLine[]>([]);
  const [discount, setDiscount] = useState("0");
  const [quote, setQuote] = useState<QuoteResult | null>(null);
  const [error, setError] = useState<string | undefined>(undefined);
  const [done, setDone] = useState<string | undefined>(undefined);

  const [itemCode, setItemCode] = useState("");
  const [locationCode, setLocationCode] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("");

  // 可選的商品（主檔）與位置（有庫存的）
  const items = catalog.data ?? [];
  const locations = (stock.data ?? []).filter(
    (row) => !itemCode || row.item_code === itemCode,
  );
  const selectedItem = items.find((row) => row.item_code === itemCode);

  function addLine() {
    if (!itemCode || !locationCode) {
      setError(t("sales.form.incomplete"));
      return;
    }
    if (lines.some((line) => line.item_code === itemCode && line.location_code === locationCode)) {
      setError(t("sales.form.duplicate"));
      return;
    }
    setError(undefined);
    setLines([
      ...lines,
      {
        item_code: itemCode,
        location_code: locationCode,
        quantity: Number(quantity || 0),
        unit_price: unitPrice || selectedItem?.suggested_price || "0",
      },
    ]);
    setItemCode("");
    setLocationCode("");
    setQuantity("1");
    setUnitPrice("");
    setQuote(null);
  }

  const quoteMutation = useMutation({
    mutationFn: () => quoteOrder(lines, Number(discount || 0)),
    onSuccess: (result) => {
      setError(undefined);
      setQuote(result);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? tError(err.code) : t("error.unknown"));
      setQuote(null);
    },
  });

  const submitMutation = useMutation({
    mutationFn: async () => {
      const order = await createSalesOrder({
        lines: lines.map((line) => ({
          item_code: line.item_code,
          location_code: line.location_code,
          quantity: line.quantity,
          unit_price: line.unit_price,
        })),
        discount_rate: Number(discount || 0),
      });
      return submitSalesOrder(order.order_no);
    },
    onSuccess: async (order) => {
      setError(undefined);
      setDone(`${t("sales.form.done")}：${order.order_no}（${order.total_paid}，毛利 ${order.total_margin}）`);
      setLines([]);
      setQuote(null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["stock"] }),
        queryClient.invalidateQueries({ queryKey: ["salesOrders"] }),
        queryClient.invalidateQueries({ queryKey: ["margins"] }),
      ]);
    },
    onError: (err) => setError(err instanceof ApiError ? tError(err.code) : t("error.unknown")),
  });

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("sales.form.title")}</CardTitle>
          <CardDescription>{t("sales.form.description")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-end gap-3">
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("sales.form.item")}</span>
              <select
                className="h-9 min-w-56 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
                value={itemCode}
                onChange={(event) => {
                  setItemCode(event.target.value);
                  setLocationCode("");
                  setUnitPrice("");
                }}
              >
                <option value="">—</option>
                {items.map((row) => (
                  <option key={row.item_code} value={row.item_code}>
                    {row.name}（{row.item_code}）
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("sales.form.location")}</span>
              <select
                className="h-9 min-w-40 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
                value={locationCode}
                onChange={(event) => setLocationCode(event.target.value)}
              >
                <option value="">—</option>
                {locations.map((row) => (
                  <option key={row.location_code} value={row.location_code}>
                    {row.warehouse_code} {row.location_code}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("sales.form.quantity")}</span>
              <input
                type="number"
                min={1}
                className="h-9 w-24 rounded-sm border border-border-strong bg-surface px-2 text-sm tabular-nums text-fg"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("sales.form.price")}</span>
              <input
                className="h-9 w-28 rounded-sm border border-border-strong bg-surface px-2 text-sm tabular-nums text-fg"
                value={unitPrice}
                placeholder={selectedItem?.suggested_price ?? "0"}
                onChange={(event) => setUnitPrice(event.target.value)}
              />
            </label>
            <Button variant="secondary" onClick={addLine}>
              {t("sales.form.add")}
            </Button>
          </div>

          {lines.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-fg-muted">
                  <th className="px-3 py-2 font-medium">{t("sales.form.item")}</th>
                  <th className="px-3 py-2 font-medium">{t("sales.form.location")}</th>
                  <th className="px-3 py-2 text-right font-medium">{t("sales.form.quantity")}</th>
                  <th className="px-3 py-2 text-right font-medium">{t("sales.form.price")}</th>
                  <th className="px-3 py-2 text-right font-medium">{t("sales.form.subtotal")}</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {lines.map((line) => (
                  <tr key={`${line.item_code}-${line.location_code}`} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 text-fg">
                      {line.item_code}
                      <span className="ml-2 text-xs text-fg-secondary">
                        {items.find((row) => row.item_code === line.item_code)?.name}
                      </span>
                    </td>
                    <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{line.location_code}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-fg">{line.quantity}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-fg">{line.unit_price}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-fg">
                      {(Number(line.unit_price) * line.quantity).toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <button
                        type="button"
                        className="text-xs text-fg-muted hover:text-danger"
                        onClick={() => {
                          setLines(lines.filter((row) => row !== line));
                          setQuote(null);
                        }}
                      >
                        {t("sales.form.remove")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-fg-muted">{t("sales.form.empty")}</p>
          )}

          <div className="flex flex-wrap items-end gap-3 border-t border-border pt-4">
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("sales.form.discount")}</span>
              <input
                type="number"
                min={0}
                max={100}
                className="h-9 w-24 rounded-sm border border-border-strong bg-surface px-2 text-sm tabular-nums text-fg"
                value={discount}
                onChange={(event) => {
                  setDiscount(event.target.value);
                  setQuote(null);
                }}
              />
            </label>
            <Button variant="secondary" disabled={lines.length === 0 || quoteMutation.isPending} onClick={() => quoteMutation.mutate()}>
              {t("sales.form.quote")}
            </Button>
            <Button
              variant="primary"
              disabled={lines.length === 0 || submitMutation.isPending}
              onClick={() => submitMutation.mutate()}
            >
              {submitMutation.isPending ? t("sales.form.submitting") : t("sales.form.submit")}
            </Button>
          </div>

          {quote ? (
            <div className="grid grid-cols-5 gap-3 rounded-sm border border-border bg-surface-raised p-4 text-sm">
              <Sum label={t("sales.summary.amount")} value={quote.total_amount} />
              <Sum label={t("sales.summary.discount")} value={quote.discount_amount} />
              <Sum label={t("sales.summary.paid")} value={quote.total_paid} />
              <Sum label={t("sales.summary.cost")} value={quote.total_cost} />
              <Sum label={t("sales.summary.margin")} value={quote.total_margin} accent />
            </div>
          ) : null}

          {error ? <p className="text-sm text-danger">{error}</p> : null}
          {done ? <p className="text-sm text-success">{done}</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}

function Sum({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-fg-muted">{label}</span>
      <span
        className={`text-lg font-semibold tabular-nums ${
          accent ? "text-accent-text" : "text-fg"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

export default SalesPage;
