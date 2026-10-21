import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { DEFAULT_LOCALE, LOCALES, catalog } from "./catalog";
import type { Locale, MessageKey } from "./catalog";

const STORAGE_KEY = "ims.locale";

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  locales: readonly Locale[];
  /** 取出訊息；缺少翻譯時 fallback 到 zh-TW，再缺則回傳 key 本身。 */
  t: (key: MessageKey) => string;
  /** 依錯誤代碼取得使用者可見文案；無對應文案時回傳通用文案。 */
  tError: (code: string | undefined) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function lookup(locale: Locale, key: string): string | undefined {
  return (catalog[locale] as Record<string, string | undefined>)[key];
}

function readStoredLocale(): Locale {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && (LOCALES as readonly string[]).includes(stored)) {
      return stored as Locale;
    }
  } catch {
    // localStorage 不可用時退回預設語系
  }
  return DEFAULT_LOCALE;
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(readStoredLocale);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, locale);
    } catch {
      // 儲存失敗不影響功能
    }
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => setLocaleState(next), []);

  const t = useCallback(
    (key: MessageKey) => lookup(locale, key) ?? lookup(DEFAULT_LOCALE, key) ?? key,
    [locale],
  );

  const tError = useCallback(
    (code: string | undefined) => {
      if (!code) return t("error.unknown");
      const key = `error.${code}` as MessageKey;
      const message = t(key);
      return message === key ? t("error.unknown") : message;
    },
    [t],
  );

  const value = useMemo(
    () => ({ locale, setLocale, locales: LOCALES, t, tError }),
    [locale, setLocale, t, tError],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n 必須在 I18nProvider 內使用。");
  }
  return context;
}

export type { Locale, MessageKey };
