import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import { ApiError, createBatch, createItem, fetchBatches, fetchItems } from "../lib/api";

/** 商品主檔：商品清單 + 新增商品；採購批次清單 + 新增批次。 */
export function CatalogPage() {
  const { t, tError } = useI18n();
  const queryClient = useQueryClient();

  const items = useQuery({ queryKey: ["items"], queryFn: () => fetchItems() });
  const batches = useQuery({ queryKey: ["batches"], queryFn: () => fetchBatches() });

  const [itemForm, setItemForm] = useState({
    name: "",
    supplier_name: "",
    suggested_price: "",
    expected_margin: "",
  });
  const [batchForm, setBatchForm] = useState({
    item_code: "",
    supplier_name: "",
    unit_price: "",
    quantity: "",
    received_at: new Date().toISOString().slice(0, 10),
  });
  const [error, setError] = useState<string | undefined>(undefined);

  const createItemMutation = useMutation({
    mutationFn: createItem,
    onSuccess: async () => {
      setError(undefined);
      setItemForm({ name: "", supplier_name: "", suggested_price: "", expected_margin: "" });
      await queryClient.invalidateQueries({ queryKey: ["items"] });
    },
    onError: (err) => setError(err instanceof ApiError ? tError(err.code) : t("error.unknown")),
  });

  const createBatchMutation = useMutation({
    mutationFn: createBatch,
    onSuccess: async () => {
      setError(undefined);
      setBatchForm({ ...batchForm, unit_price: "", quantity: "" });
      await queryClient.invalidateQueries({ queryKey: ["batches"] });
    },
    onError: (err) => setError(err instanceof ApiError ? tError(err.code) : t("error.unknown")),
  });

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("catalog.items.title")}</CardTitle>
          <CardDescription>{t("catalog.items.description")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-fg-muted">
                <th className="px-3 py-2 font-medium">{t("catalog.items.code")}</th>
                <th className="px-3 py-2 font-medium">{t("catalog.items.name")}</th>
                <th className="px-3 py-2 font-medium">{t("catalog.items.supplier")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("catalog.items.price")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("catalog.items.margin")}</th>
              </tr>
            </thead>
            <tbody>
              {(items.data ?? []).map((item) => (
                <tr key={item.item_code} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{item.item_code}</td>
                  <td className="px-3 py-2 text-fg">{item.name}</td>
                  <td className="px-3 py-2 text-fg-secondary">{item.supplier_name}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-fg">{item.suggested_price}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-fg">{item.expected_margin}</td>
                </tr>
              ))}
              {(items.data ?? []).length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-center text-fg-muted">
                    {t("catalog.items.empty")}
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>

          <div className="flex flex-wrap items-end gap-3 border-t border-border pt-4">
            <Field
              label={t("catalog.items.name")}
              value={itemForm.name}
              onChange={(v) => setItemForm({ ...itemForm, name: v })}
            />
            <Field
              label={t("catalog.items.supplier")}
              value={itemForm.supplier_name}
              onChange={(v) => setItemForm({ ...itemForm, supplier_name: v })}
            />
            <Field
              label={t("catalog.items.price")}
              value={itemForm.suggested_price}
              onChange={(v) => setItemForm({ ...itemForm, suggested_price: v })}
            />
            <Field
              label={t("catalog.items.margin")}
              value={itemForm.expected_margin}
              onChange={(v) => setItemForm({ ...itemForm, expected_margin: v })}
            />
            <Button
              variant="primary"
              disabled={createItemMutation.isPending}
              onClick={() =>
                createItemMutation.mutate({
                  name: itemForm.name,
                  supplier_name: itemForm.supplier_name,
                  suggested_price: itemForm.suggested_price || "0",
                  expected_margin: itemForm.expected_margin || "0",
                })
              }
            >
              {t("catalog.items.create")}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("catalog.batches.title")}</CardTitle>
          <CardDescription>{t("catalog.batches.description")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-fg-muted">
                <th className="px-3 py-2 font-medium">{t("catalog.batches.po")}</th>
                <th className="px-3 py-2 font-medium">{t("catalog.batches.item")}</th>
                <th className="px-3 py-2 font-medium">{t("catalog.batches.date")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("catalog.batches.price")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("catalog.batches.quantity")}</th>
                <th className="px-3 py-2 text-right font-medium">{t("catalog.batches.total")}</th>
              </tr>
            </thead>
            <tbody>
              {(batches.data ?? []).map((batch) => (
                <tr key={batch.po_number} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-mono text-xs text-fg-secondary">{batch.po_number}</td>
                  <td className="px-3 py-2 text-fg">
                    {batch.item_name}
                    <span className="ml-2 font-mono text-xs text-fg-muted">{batch.item_code}</span>
                  </td>
                  <td className="px-3 py-2 text-fg-secondary">{batch.received_at}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-fg">{batch.unit_price}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-fg">{batch.quantity}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-fg">{batch.total}</td>
                </tr>
              ))}
              {(batches.data ?? []).length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-3 py-6 text-center text-fg-muted">
                    {t("catalog.batches.empty")}
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>

          <div className="flex flex-wrap items-end gap-3 border-t border-border pt-4">
            <label className="flex flex-col gap-1.5 text-sm">
              <span className="text-fg-secondary">{t("catalog.batches.item")}</span>
              <select
                className="h-9 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
                value={batchForm.item_code}
                onChange={(event) => setBatchForm({ ...batchForm, item_code: event.target.value })}
              >
                <option value="">—</option>
                {(items.data ?? []).map((item) => (
                  <option key={item.item_code} value={item.item_code}>
                    {item.name}（{item.item_code}）
                  </option>
                ))}
              </select>
            </label>
            <Field
              label={t("catalog.batches.supplier")}
              value={batchForm.supplier_name}
              onChange={(v) => setBatchForm({ ...batchForm, supplier_name: v })}
            />
            <Field
              label={t("catalog.batches.price")}
              value={batchForm.unit_price}
              onChange={(v) => setBatchForm({ ...batchForm, unit_price: v })}
            />
            <Field
              label={t("catalog.batches.quantity")}
              value={batchForm.quantity}
              onChange={(v) => setBatchForm({ ...batchForm, quantity: v })}
            />
            <Field
              label={t("catalog.batches.date")}
              value={batchForm.received_at}
              onChange={(v) => setBatchForm({ ...batchForm, received_at: v })}
            />
            <Button
              variant="primary"
              disabled={createBatchMutation.isPending}
              onClick={() =>
                createBatchMutation.mutate({
                  item_code: batchForm.item_code,
                  supplier_name: batchForm.supplier_name,
                  unit_price: batchForm.unit_price || "0",
                  quantity: Number(batchForm.quantity || 0),
                  received_at: batchForm.received_at,
                })
              }
            >
              {t("catalog.batches.create")}
            </Button>
          </div>

          {error ? <p className="text-sm text-danger">{error}</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm">
      <span className="text-fg-secondary">{label}</span>
      <input
        className="h-9 rounded-sm border border-border-strong bg-surface px-2 text-sm text-fg"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

export default CatalogPage;
