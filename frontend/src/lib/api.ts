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
