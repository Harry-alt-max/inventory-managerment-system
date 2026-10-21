import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "../features/auth";
import { useI18n } from "../i18n";
import { ApiError } from "../lib/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

/**
 * 登入頁（EXPERIENCE.md「登入表單」）。
 *
 * - 置中卡片、單欄；標籤在欄位上方、錯誤在欄位下方（danger token）
 * - 送出後密碼欄清空、帳號欄保留
 * - 錯誤文案由後端的機器可讀 code 對應到 message catalog（AD-33）
 */
export function LoginPage() {
  const { t, tError } = useI18n();
  const { signIn } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorCode, setErrorCode] = useState<string | undefined>(undefined);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setErrorCode(undefined);
    setFieldErrors({});
    try {
      await signIn(username.trim(), password);
      setPassword("");
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorCode(error.code);
        setFieldErrors(error.fieldErrors);
      } else {
        setErrorCode("system.internal_error");
      }
      // 密碼欄清空、帳號欄保留（EXPERIENCE.md 登入表單行為）
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{t("auth.title")}</CardTitle>
          <CardDescription>{t("auth.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit} noValidate>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-fg" htmlFor="login-username">
                {t("auth.username")}
              </label>
              <input
                id="login-username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="h-9 w-full rounded-sm border border-border-strong bg-surface px-3 text-sm text-fg placeholder:text-fg-muted"
                placeholder={t("auth.username.placeholder")}
              />
              {fieldErrors.username ? (
                <span className="text-xs text-danger">{fieldErrors.username.join("、")}</span>
              ) : null}
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-fg" htmlFor="login-password">
                {t("auth.password")}
              </label>
              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-9 w-full rounded-sm border border-border-strong bg-surface px-3 text-sm text-fg placeholder:text-fg-muted"
                placeholder={t("auth.password.placeholder")}
              />
              {fieldErrors.password ? (
                <span className="text-xs text-danger">{fieldErrors.password.join("、")}</span>
              ) : null}
            </div>

            {errorCode ? (
              <div role="alert" className="rounded-sm border border-danger-tint bg-danger-tint p-3">
                <p className="text-sm text-danger">{tError(errorCode)}</p>
                <p className="mt-1 text-xs text-fg-muted">
                  {t("error.code")}: <span className="font-mono">{errorCode}</span>
                </p>
              </div>
            ) : null}

            <Button type="submit" variant="primary" disabled={submitting} className="w-full">
              {submitting ? t("auth.submitting") : t("auth.submit")}
            </Button>

            <p className="text-xs text-fg-muted">{t("auth.hint")}</p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default LoginPage;
