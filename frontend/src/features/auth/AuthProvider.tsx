import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { fetchCurrentUser, login as loginRequest, loginAsRole, logout as logoutRequest } from "../../lib/api";
import type { AuthUser } from "../../lib/api";

export type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: AuthUser | null;
  status: AuthStatus;
  /** 以帳號密碼登入；成功後更新身分狀態。 */
  signIn: (username: string, password: string) => Promise<void>;
  /** 以角色直接進入（示範模式）。 */
  signInAsRole: (role: string) => Promise<void>;
  /** 登出；結束後回到登入頁。 */
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * 認證狀態（AD-6：session + CSRF 是唯一認證機制）。
 *
 * 掛載時以 `GET /auth/me` 還原 session；未登入回 401 即視為匿名。
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  useEffect(() => {
    const controller = new AbortController();
    fetchCurrentUser(controller.signal)
      .then((current) => {
        setUser(current);
        setStatus(current ? "authenticated" : "anonymous");
      })
      .catch(() => {
        setUser(null);
        setStatus("anonymous");
      });
    return () => controller.abort();
  }, []);

  const signIn = useCallback(async (username: string, password: string) => {
    const current = await loginRequest(username, password);
    setUser(current);
    setStatus("authenticated");
  }, []);

  const signInAsRole = useCallback(async (role: string) => {
    const current = await loginAsRole(role);
    setUser(current);
    setStatus("authenticated");
  }, []);

  const signOut = useCallback(async () => {
    await logoutRequest();
    setUser(null);
    setStatus("anonymous");
  }, []);

  const value = useMemo(
    () => ({ user, status, signIn, signInAsRole, signOut }),
    [user, status, signIn, signInAsRole, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth 必須在 AuthProvider 內使用。");
  }
  return context;
}
