"use client";

import { useLanguage } from "@/i18n/language-provider";
import { locales, type Locale } from "@/i18n/config";

export function LanguageToggle() {
  const { locale, setLocale, isDevelopment } = useLanguage();

  if (!isDevelopment) return null;

  return (
    <div className="flex gap-1">
      {locales.map((l) => (
        <button
          key={l}
          onClick={() => setLocale(l)}
          className={`px-2 py-0.5 text-xs uppercase rounded ${
            locale === l
              ? "font-bold underline text-white"
              : "text-[#858585] hover:text-white"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
