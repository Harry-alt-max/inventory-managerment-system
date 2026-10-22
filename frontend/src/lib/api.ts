/**
 * 後端 API 客戶端。
 *
 * 契約（AD-7、AD-17）：
 * - 路徑前綴 `/api/v1/`
 * - 錯誤回應一律為 `{code, detail, field_errors}`
 * - 後端只回機器可讀 `code`，使用者可見文案由前端 catalog 本地化
 * - 認證以 session + CSRF 為唯一機制（AD-6）
 */

export const API_BASE = "/api/v1";

export interface ApiErrorEnvelope {
  code: string;
  detail: string;
  field_errors: Record<string, string[]>;
}

export interface HealthResponse {
  status: string;
  version: string;
}

/** 登入者身分（後端 accounts.services.describe_user 的回應形狀）。 */
export interface AuthUser {
  id: number;
  username: string;
  display_name: string;
  /** 角色代碼：warehouse / purchasing / sales / accounting。 */
  roles: string[];
}

export interface Item {
  item_code: string;
  name: string;
  supplier_name: string;
  suggested_price: string;
  expected_margin: string;
}

export interface Batch {
  po_number: string;
  item_code: string;
  item_name: string;
  supplier_name: string;
  unit_price: string;
  quantity: number;
  total: string;
  received_at: string;
}

export interface Warehouse {
  code: string;
  name: string;
}

export interface Location {
  code: string;
  name: string;
  warehouse_code: string;
}

export interface StockRow {
  item_code: string;
  item_name: string;
  location_code: string;
  location_name: string;
  warehouse_code: string;
  warehouse_name: string;
  quantity: number;
  updated_at: string;
}

export interface Movement {
  id: number;
  item_code: string;
  item_name: string;
  location_code: string;
  warehouse_code: string;
  batch_po_number: string | null;
  quantity: number;
  purpose: string;
  actor_username: string;
  occurred_at: string;
  note: string;
}

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly fieldErrors: Record<string, string[]>;

  constructor(code: string, detail: string, status: number, fieldErrors: Record<string, string[]> = {}) {
    super(detail);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

function isEnvelope(payload: unknown): payload is ApiErrorEnvelope {
  return (
    typeof payload === "object" &&
    payload !== null &&
    typeof (payload as Partial<ApiErrorEnvelope>).code === "string"
  );
}

/** 讀取 Django 設定的 csrftoken cookie（double-submit 的一半）。 */
export function readCsrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      credentials: "same-origin",
      ...init,
      headers: { Accept: "application/json", ...(init.headers ?? {}) },
    });
  } catch {
    throw new ApiError("network.unreachable", "Network request failed.", 0);
  }

  const raw = await response.text();
  let payload: unknown = null;
  if (raw) {
    try {
      payload = JSON.parse(raw);
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    if (isEnvelope(payload)) {
      throw new ApiError(payload.code, payload.detail, response.status, payload.field_errors ?? {});
    }
    // 開發代理或反向代理無法連到後端時（例如 502/503/504），視為連線失敗
    const unreachable = response.status === 502 || response.status === 503 || response.status === 504;
    throw new ApiError(
      unreachable ? "network.unreachable" : "system.internal_error",
      response.statusText || "Request failed.",
      response.status,
    );
  }

  return payload as T;
}

/** 取得後端健康檢查結果；連線失敗時拋出 ApiError（code = network.unreachable）。 */
export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health", { signal });
}

/** 取得 CSRF token（同時會由後端設定 csrftoken cookie）。 */
export async function fetchCsrfToken(): Promise<string> {
  const payload = await apiFetch<{ csrf_token: string }>("/auth/csrf", { method: "GET" });
  return payload.csrf_token || readCsrfToken();
}

/** 以帳號密碼登入（需要 X-CSRFToken 標頭）。 */
export async function login(username: string, password: string): Promise<AuthUser> {
  const token = await fetchCsrfToken();
  const payload = await apiFetch<{ user: AuthUser }>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    body: JSON.stringify({ username, password }),
  });
  return payload.user;
}

/** 以角色直接進入（示範模式；正式環境未開放）。 */
export async function loginAsRole(role: string): Promise<AuthUser> {
  const token = await fetchCsrfToken();
  const payload = await apiFetch<{ user: AuthUser }>("/auth/login-as", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    body: JSON.stringify({ role }),
  });
  return payload.user;
}

/** 登出（結束 session）。 */
export async function logout(): Promise<void> {
  const token = readCsrfToken() || (await fetchCsrfToken());
  await apiFetch<{ status: string }>("/auth/logout", {
    method: "POST",
    headers: { "X-CSRFToken": token },
  });
}

/** 取得目前登入者；未登入回 null。 */
export async function fetchCurrentUser(signal?: AbortSignal): Promise<AuthUser | null> {
  try {
    const payload = await apiFetch<{ user: AuthUser }>("/auth/me", { signal });
    return payload.user;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

// ---------------------------------------------------------------------------
// 寫入型呼叫（需要 CSRF token）
// ---------------------------------------------------------------------------

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const token = readCsrfToken() || (await fetchCsrfToken());
  return apiFetch<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// 商品主檔、批次、倉庫與位置
// ---------------------------------------------------------------------------

export async function fetchItems(query = ""): Promise<Item[]> {
  const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
  const payload = await apiFetch<{ items: Item[] }>(`/items${suffix}`);
  return payload.items;
}

export async function createItem(input: {
  name: string;
  supplier_name: string;
  suggested_price: string;
  expected_margin: string;
}): Promise<Item> {
  const payload = await postJson<{ item: Item }>("/items", input);
  return payload.item;
}

export async function fetchBatches(): Promise<Batch[]> {
  const payload = await apiFetch<{ batches: Batch[] }>("/batches");
  return payload.batches;
}

export async function createBatch(input: {
  item_code: string;
  supplier_name: string;
  unit_price: string;
  quantity: number;
  received_at: string;
}): Promise<Batch> {
  const payload = await postJson<{ batch: Batch }>("/batches", input);
  return payload.batch;
}

export async function fetchWarehouses(): Promise<Warehouse[]> {
  const payload = await apiFetch<{ warehouses: Warehouse[] }>("/warehouses");
  return payload.warehouses;
}

export async function createWarehouse(input: { code: string; name: string }): Promise<Warehouse> {
  const payload = await postJson<{ warehouse: Warehouse }>("/warehouses", input);
  return payload.warehouse;
}

export async function fetchLocations(warehouseCode: string): Promise<Location[]> {
  const payload = await apiFetch<{ locations: Location[] }>(
    `/warehouses/${encodeURIComponent(warehouseCode)}/locations`,
  );
  return payload.locations;
}

export async function createLocation(
  warehouseCode: string,
  input: { code: string; name: string },
): Promise<Location> {
  const payload = await postJson<{ location: Location }>(
    `/warehouses/${encodeURIComponent(warehouseCode)}/locations`,
    input,
  );
  return payload.location;
}

// ---------------------------------------------------------------------------
// 庫存現況、异動與入庫
// ---------------------------------------------------------------------------

export async function fetchStock(query = ""): Promise<StockRow[]> {
  const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
  const payload = await apiFetch<{ stock: StockRow[] }>(`/stock${suffix}`);
  return payload.stock;
}

export async function fetchMovements(): Promise<Movement[]> {
  const payload = await apiFetch<{ movements: Movement[] }>("/stock/movements");
  return payload.movements;
}

export async function createInbound(input: {
  item_code: string;
  location_code: string;
  batch_po_number: string;
  quantity: number;
  note?: string;
}): Promise<Movement> {
  const payload = await postJson<{ movement: Movement }>("/stock/inbound", input);
  return payload.movement;
}

// ---------------------------------------------------------------------------
// 銷貨單與毛利
// ---------------------------------------------------------------------------

export interface QuoteLine {
  item_code: string;
  item_name: string;
  location_code: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
  cost: string;
  consumptions: {
    po_number: string;
    quantity: number;
    unit_price: string;
    cost: string;
  }[];
}

export interface QuoteResult {
  lines: QuoteLine[];
  total_amount: string;
  discount_rate: string;
  discount_amount: string;
  total_paid: string;
  total_cost: string;
  total_margin: string;
}

export interface SalesOrderLineView {
  item_code: string;
  item_name: string;
  location_code: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
  cost: string;
  consumptions: {
    po_number: string;
    quantity: number;
    unit_price: string;
    cost: string;
  }[];
}

export interface SalesOrderView {
  order_no: string;
  status: string;
  status_label: string;
  discount_rate: string;
  total_amount: string;
  discount_amount: string;
  total_paid: string;
  total_cost: string;
  total_margin: string;
  created_by: string;
  created_at: string;
  submitted_at: string | null;
  note: string;
  lines: SalesOrderLineView[];
}

export async function quoteOrder(
  lines: { item_code: string; location_code: string; quantity: number; unit_price?: string }[],
  discountRate: number,
): Promise<QuoteResult> {
  return postJson<QuoteResult>("/sales/quote", { lines, discount_rate: discountRate });
}

export async function fetchSalesOrders(params: {
  order_no?: string;
  date_from?: string;
  date_to?: string;
} = {}): Promise<SalesOrderView[]> {
  const query = new URLSearchParams();
  if (params.order_no) query.set("order_no", params.order_no);
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const payload = await apiFetch<{ orders: SalesOrderView[] }>(`/sales/orders${suffix}`);
  return payload.orders;
}

export async function createSalesOrder(input: {
  lines: { item_code: string; location_code: string; quantity: number; unit_price?: string }[];
  discount_rate: number;
  note?: string;
}): Promise<SalesOrderView> {
  const payload = await postJson<{ order: SalesOrderView }>("/sales/orders", input);
  return payload.order;
}

export async function submitSalesOrder(orderNo: string): Promise<SalesOrderView> {
  const payload = await postJson<{ order: SalesOrderView }>(
    `/sales/orders/${encodeURIComponent(orderNo)}/submit`,
    {},
  );
  return payload.order;
}

export async function reverseSalesOrder(orderNo: string): Promise<SalesOrderView> {
  const payload = await postJson<{ order: SalesOrderView }>(
    `/sales/orders/${encodeURIComponent(orderNo)}/reverse`,
    {},
  );
  return payload.order;
}

export async function fetchMargins(params: {
  order_no?: string;
  date_from?: string;
  date_to?: string;
} = {}): Promise<SalesOrderView[]> {
  const query = new URLSearchParams();
  if (params.order_no) query.set("order_no", params.order_no);
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const payload = await apiFetch<{ orders: SalesOrderView[] }>(`/sales/margins${suffix}`);
  return payload.orders;
}
