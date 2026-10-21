import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import { ApiError, createInbound, fetchBatches, fetchMovements, fetchStock } from "../lib/api";

/** 入庫作業：選商品、位置、批次與數量即可入庫（AD-11）。 */
export function InboundPage() {
  const { t, tError } = useI18n();
  const queryClient = useQueryClient();

  const stock = useQuery({ queryKey: ["stock"], queryFn: () => fetchStock() });
  const batches = useQuery({ queryKey: ["batches"], queryFn: () => fetchBatches() });

  const [form, setForm] = useState({ item_code: "", location_code: "", batch_po_number: "", quantity: "" });
  const [error, setError] = useState<string | undefined>(undefined);
  const [done, setDone] = useState<string | undefined>(undefined);

  // 可入庫的位置：依已選商品過濾庫存現況
  const locations = (stock.data ?? [])
    .filter((row) => !form.item_code || row.item_code === form.item_code)
    .map((row) => ({ code: row.location_code, label: `${row.warehouse_code} ${row.location_code}` }));

  // 可用批次：依已選商品過濾
  const itemBatches = (batches.data ?? []).filter(
    (batch) => !form.item_code || batch.item_code === form.item_code,
  );

  const inbound = useMutation({
    mutationFn: createInbound,
    onSuccess: async (movement) => {
      setError(undefined);
      setDone(
        `${t("stock.inbound.success")}：${movement.item_code} × ${movement.quantity} → ${movement.location_code}`,
      );
      setForm({ item_code: "", location_code: "", batch_po_number: "", quantity: "" });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["stock"] }),
        queryClient.invalidateQueries({ queryKey: ["movements"] }),
      ]);
    },
    onError: (err) => {
      setDone(undefined);
      setError(err instanceof ApiError ? tError(err.code) : t("error.unknown"));
    },
  });

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("stock.inbound.title")}</CardTitle>
          <CardDescription>{t("stock.inbound.description")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-end gap-3">
            <Select
              label={t("stock.inbound.item")}
              value={form.item_code}
              onChange={(value) => setForm({ ...form, item_code: value, location_code: "", batch_po_number: "" })}
              options={[
                { value: "", label: "—" },
                ...(stock.data ?? []).map((row) => ({
                  value: row.item_code,
                  label: `${row.item_name}（${row.item_code}）`,
                })),
              ]}
            />
            <Select
              label={t("stock.inbound.location")}
              value={form.location_code}
              onChange={(value) => setForm({ ...form, location_code: value })}
              options={[
                { value: "", label: "—" },
                ...locations.map((row) => ({ value: row.code, label: row.label })),
              ]}
            />
            <Select
              label={t("stock.inbound.batch")}
              value={form.batch_po_number}
              onChange={(value) => setForm({ ...form, batch_po_number: value })}
              options={[
                { value: "", label: "—" },
                ...itemBatches.map((batch) => ({
                  value: batch.po_number,
                  label: `${batch.po_number}（${batch.item_name}）`,
                })),
              ]}
            />
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("stock.inbound.quantity")}</span>
              <input
                type="number"
                min={1}
                className="h-9 w-28 rounded-sm border border-border-strong bg-surface px-2 text-sm tabular-nums text-fg"
                value={form.quantity}
                onChange={(event) => setForm({ ...form, quantity: event.target.value })}
              />
            </label>
            <Button
              variant="primary"
              disabled={inbound.isPending}
              onClick={() =>
                inbound.mutate({
                  item_code: form.item_code,
                  location_code: form.location_code,
                  batch_po_number: form.batch_po_number,
                  quantity: Number(form.quantity || 0),
                })
              }
            >
              {t("stock.inbound.submit")}
            </Button>
          </div>

          {error ? <p className="text-sm text-danger">{error}</p> : null}
          {done ? <p className="text-sm text-success">{done}</p> : null}
        </CardContent>
      </Card>

      <MovementTable />
    </div>
  );
}

/** 庫存異動紀錄（僅追加，AD-12）。 */
export function MovementTable() {
  const { t } = useI18n();
  const movements = useQuery({ queryKey: ["movements"], queryFn: () => fetchMovements() });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("stock.movements.title")}</CardTitle>
        <CardDescription>{t("stock.movements.description")}</CardDescription>
      </CardHeader>
      <CardContent>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-fg-muted">
              <th className="px-3 py-2 font-medium">{t("stock.movements.time")}</th>
              <th className="px-3 py-2 font-medium">{t("stock.movements.item")}</th>
              <th className="px-3 py-2 font-medium">{t("stock.movements.location")}</th>
              <th className="px-3 py-2 font-medium">{t("stock.movements.batch")}</th>
              <th className="px-3 py-2 text-right font-medium">{t("stock.movements.quantity")}</th>
              <th className="px-3 py-2 font-medium">{t("stock.movements.actor")}</th>
            </tr>
          </thead>
          <tbody>
            {(movements.data ?? []).map((movement) => (
              <tr key={movement.id} className="border-b border-border last:border-0">
                <td className="px-3 py-2 text-fg-secondary">
                  {new Date(movement.occurred_at).toLocaleString("zh-TW", {
                    hour12: false,
                    timeZone: "Asia/Taipei",
                  })}
                </td>
                <td className="px-3 py-2 text-fg">
                  {movement.item_name}
                  <span className="ml-2 font-mono text-xs text-fg-muted">{movement.item_code}</span>
                </td>
                <td className="px-3 py-2 text-fg-secondary">{movement.location_code}</td>
                <td className="px-3 py-2 font-mono text-xs text-fg-secondary">
                  {movement.batch_po_number ?? "—"}
                </td>
                <td
                  className={`px-3 py-2 text-right tabular-nums ${
                    movement.quantity >= 0 ? "text-success" : "text-fg"
                  }`}
                >
                  {movement.quantity > 0 ? `+${movement.quantity}` : movement.quantity}
                </td>
                <td className="px-3 py-2 text-fg-secondary">{movement.actor_username}</td>
              </tr>
            ))}
            {(movements.data ?? []).length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-fg-muted">
                  {t("stock.movements.empty")}
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm">
      <span className="text-fg-secondary">{label}</span>
      <select
        className="h-9 min-w-56 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export default InboundPage;
