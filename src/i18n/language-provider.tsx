"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { type Locale, defaultLocale } from "./config";

interface LanguageContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  isDevelopment: boolean;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function getStoredLocale(): Locale {
  if (typeof window === "undefined") return defaultLocale;

  const stored = localStorage.getItem("locale");
  if (stored === "sk" || stored === "en") return stored;

  const attr = document.documentElement.getAttribute("data-default-locale");
  if (attr === "sk" || attr === "en") return attr;

  return defaultLocale;
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const isDevelopment = process.env.NODE_ENV === "development";

  useEffect(() => {
    const stored = getStoredLocale();
    if (stored !== defaultLocale) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- mount-time sync from localStorage; avoids hydration mismatch vs lazy init
      setLocaleState(stored);
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    localStorage.setItem("locale", next);
    document.documentElement.lang = next;
  }, []);

  return (
    <LanguageContext.Provider value={{ locale, setLocale, isDevelopment }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return ctx;
}
