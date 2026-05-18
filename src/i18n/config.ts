export const locales = ['sk', 'en'] as const;

export type Locale = (typeof locales)[number];

export const defaultLocale: Locale =
  process.env.NODE_ENV === 'development' ? 'en' : 'sk';
