"use client";

import { useLanguage } from "./language-provider";
import en from "./messages/en.json";
import sk from "./messages/sk.json";

const dictionaries: Record<string, Record<string, unknown>> = { en, sk };

function getNestedValue(obj: Record<string, unknown>, path: string): string | undefined {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current == null || typeof current !== "object") return undefined;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === "string" ? current : undefined;
}

export function useTranslations(namespace?: string) {
  const { locale } = useLanguage();
  const dict = dictionaries[locale] ?? dictionaries["en"];

  return function t(key: string, params?: Record<string, string | number>): string {
    const fullKey = namespace ? `${namespace}.${key}` : key;
    let value = getNestedValue(dict, fullKey) ?? getNestedValue(dictionaries["en"], fullKey) ?? fullKey;
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        value = value.replace(`{${k}}`, String(v));
      }
    }
    return value;
  };
}
