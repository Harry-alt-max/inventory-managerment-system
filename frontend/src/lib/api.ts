/**
 * 後端 API 客戶端。
 *
 * 契約（AD-7、AD-17）：
 * - 路徑前綴 `/api/v1/`
 * - 錯誤回應一律為 `{code, detail, field_errors}`
 * - 後端只回機器可讀 `code`，使用者可見文案由前端 catalog 本地化
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

/** 取得後端健康檢查結果；連線失敗時拋出 ApiError（code = network.unreachable）。 */
export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/health`, {
      signal,
      headers: { Accept: "application/json" },
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

  return payload as HealthResponse;
}
