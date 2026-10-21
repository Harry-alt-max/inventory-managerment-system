import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, RefreshCw } from "lucide-react";

import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useI18n } from "../i18n";
import { ApiError, fetchHealth } from "../lib/api";

/**
 * 首頁：以 TanStack Query 呼叫 `GET /api/v1/health`，
 * 顯示後端版本字串，作為後端 → 前端 → 資料庫的最小連線驗證。
 * 後端不可達時顯示明確的失敗訊息與重試鈕（不得空白頁）。
 */
export function HomePage() {
  const { t, tError } = useI18n();

  const health = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => fetchHealth(signal),
    retry: 1,
    staleTime: 30_000,
  });

  const errorCode = health.error instanceof ApiError ? health.error.code : undefined;

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-12 gap-4">
        <Card className="col-span-6">
          <CardHeader>
            <CardTitle>{t("home.card.status")}</CardTitle>
            <CardDescription>{t("home.description")}</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            {health.isPending ? (
              <Badge tone="neutral">{t("home.status.checking")}</Badge>
            ) : health.isError ? (
              <Badge tone="danger">{t("home.status.unavailable")}</Badge>
            ) : (
              <Badge tone="success">{t("home.status.ok")}</Badge>
            )}
            {health.isFetching && !health.isPending ? (
              <RefreshCw size={16} strokeWidth={1.5} aria-hidden="true" className="animate-spin text-fg-muted" />
            ) : null}
          </CardContent>
        </Card>

        <Card className="col-span-6">
          <CardHeader>
            <CardTitle>{t("home.card.version")}</CardTitle>
            <CardDescription>{t("health.version.label")}</CardDescription>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-xxl font-semibold tabular-nums text-fg">
              {health.data?.version ?? t("common.dash")}
            </span>
          </CardContent>
        </Card>
      </div>

      {health.isError ? (
        <Card className="border-danger-tint bg-danger-tint">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-danger">
              <AlertTriangle size={20} strokeWidth={1.5} aria-hidden="true" />
              {t("error.title")}
            </CardTitle>
            <CardDescription className="text-danger">
              {tError(errorCode)}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <span className="text-xs text-fg-muted">
              {t("error.code")}: <span className="font-mono">{errorCode ?? "unknown"}</span>
            </span>
            <span className="text-sm text-fg-secondary">{t("home.hint")}</span>
            <div>
              <Button variant="primary" size="sm" onClick={() => void health.refetch()}>
                <RefreshCw size={16} strokeWidth={1.5} aria-hidden="true" />
                {t("home.status.retry")}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

export default HomePage;
