/**
 * LanguageContext — Global i18n state
 *
 * Stores the current locale and exposes a `t(key)` helper
 * that resolves dot-notated keys against the active JSON file.
 *
 * Usage:
 *   const { t, locale, setLocale } = useLanguage();
 *   t("nav.markets")  // → "Markets" | "市场" | "Mercados"
 */

import { createContext, useState, useCallback, useMemo } from "react";
import en from "../i18n/en.json";
import zh from "../i18n/zh.json";
import es from "../i18n/es.json";

const LOCALES = { en, zh, es };
const LOCALE_LABELS = {
  en: { label: "English", flag: "EN" },
  zh: { label: "中文", flag: "中" },
  es: { label: "Español", flag: "ES" },
};

const STORAGE_KEY = "cryptoscope_lang";

function getInitialLocale() {
  if (typeof window === "undefined") return "en";
  return localStorage.getItem(STORAGE_KEY) || "en";
}

export const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [locale, setLocaleState] = useState(getInitialLocale);

  const setLocale = useCallback((code) => {
    setLocaleState(code);
    localStorage.setItem(STORAGE_KEY, code);
  }, []);

  // Resolve dot-notated key: "nav.markets" → translations.nav.markets
  const t = useCallback(
    (key) => {
      const dict = LOCALES[locale] || LOCALES.en;
      const parts = key.split(".");
      let result = dict;
      for (const part of parts) {
        result = result?.[part];
        if (result === undefined) return key; // fallback: return key itself
      }
      return result;
    },
    [locale]
  );

  const value = useMemo(
    () => ({ locale, setLocale, t, localeLabels: LOCALE_LABELS }),
    [locale, setLocale, t]
  );

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}
