## Purpose

Provides the internationalization (i18n) foundation for the application, including next-intl configuration, translation dictionaries, a LanguageProvider React context, and a parity check script.

## Requirements

### Requirement: next-intl installed and configured
The project SHALL have `next-intl` as a dependency in `package.json`. A file `src/i18n/config.ts` SHALL export `locales` (array `['sk', 'en']`), `Locale` type, and a default locale derived from environment: `'en'` when `NODE_ENV === 'development'`, `'sk'` otherwise.

#### Scenario: next-intl in package.json
- **WHEN** `package.json` is inspected
- **THEN** `next-intl` SHALL be listed in `dependencies`

#### Scenario: Config exports correct locales
- **WHEN** `src/i18n/config.ts` is imported
- **THEN** it SHALL export `locales` as `['sk', 'en']` and `Locale` as a union type of those values

#### Scenario: Dev default is English
- **WHEN** `NODE_ENV` is `"development"`
- **THEN** the default locale SHALL be `"en"`

#### Scenario: Production default is Slovak
- **WHEN** `NODE_ENV` is `"production"`
- **THEN** the default locale SHALL be `"sk"`

### Requirement: Translation dictionaries with identical key structures
Two JSON files SHALL exist at `src/i18n/messages/en.json` and `src/i18n/messages/sk.json`. Both files SHALL have identical key structures (same nested keys, same leaf count). Every leaf value SHALL be a non-empty string. The dictionaries SHALL cover all user-facing strings from: sidebar (title, placeholder, greeting, suggestions), designs (heading, empty state, labels, params), pricing (all row labels, tooltips, totals, error), alerts (file too large, upload limit, parse errors), and metadata (title, description).

#### Scenario: Both dictionary files exist
- **WHEN** the filesystem is checked
- **THEN** both `src/i18n/messages/en.json` and `src/i18n/messages/sk.json` SHALL exist and be valid JSON

#### Scenario: Key structures are identical
- **WHEN** the flattened keys of `en.json` and `sk.json` are compared
- **THEN** the sets SHALL be identical — no keys present in one but missing from the other

#### Scenario: No empty translation values
- **WHEN** any leaf value in either dictionary is inspected
- **THEN** it SHALL be a non-empty string

#### Scenario: Sidebar strings are present
- **WHEN** `en.json` is inspected for `sidebar.title`, `sidebar.placeholder`, `sidebar.greeting`
- **THEN** all three keys SHALL exist with non-empty English string values

#### Scenario: Slovak sidebar strings use Slovak text
- **WHEN** `sk.json` is inspected for `sidebar.title`, `sidebar.placeholder`, `sidebar.greeting`
- **THEN** all three keys SHALL exist with Slovak-language string values (not English)

### Requirement: LanguageProvider React context
A file `src/i18n/language-provider.tsx` SHALL export a `LanguageProvider` component and a `useLanguage` hook. The provider SHALL accept `children` and manage `locale` state. On mount, it SHALL read the saved locale from `localStorage` key `"locale"`; if absent, it SHALL derive the default from the `data-default-locale` attribute on `<html>`. The `setLocale` function SHALL update state, persist to `localStorage`, and set `document.documentElement.lang`. The `useLanguage` hook SHALL return `{ locale, setLocale, isDevelopment }`.

#### Scenario: Provider reads saved locale from localStorage
- **WHEN** `LanguageProvider` mounts and `localStorage.getItem('locale')` returns `"sk"`
- **THEN** the provider's `locale` state SHALL be `"sk"`

#### Scenario: Provider falls back to HTML attribute
- **WHEN** `LanguageProvider` mounts and `localStorage` has no `"locale"` entry and `<html data-default-locale="sk">`
- **THEN** the provider's `locale` state SHALL be `"sk"`

#### Scenario: setLocale persists and updates DOM
- **WHEN** `setLocale("en")` is called
- **THEN** `localStorage.getItem('locale')` SHALL return `"en"` and `document.documentElement.lang` SHALL be `"en"`

#### Scenario: useLanguage returns isDevelopment flag
- **WHEN** `useLanguage()` is called during `NODE_ENV=development`
- **THEN** `isDevelopment` SHALL be `true`

### Requirement: i18n parity check script
A file `scripts/check-i18n-parity.mjs` SHALL exist and be callable via `npm run i18n:check`. It SHALL flatten and compare keys between `en.json` and `sk.json`. If any key exists in one but not the other, it SHALL print the missing keys to stderr and exit with code 1. If keys match, it SHALL print a success message and exit 0.

#### Scenario: Parity check passes when keys match
- **WHEN** `npm run i18n:check` is run and both dictionaries have identical keys
- **THEN** the script SHALL exit with code 0 and print a success message

#### Scenario: Parity check fails when keys differ
- **WHEN** `npm run i18n:check` is run and `en.json` has a key `sidebar.newKey` missing from `sk.json`
- **THEN** the script SHALL print "Missing in sk.json: sidebar.newKey" to stderr and exit with code 1

#### Scenario: Parity check detects extra keys
- **WHEN** `npm run i18n:check` is run and `sk.json` has a key `sidebar.extra` not in `en.json`
- **THEN** the script SHALL print "Extra in sk.json: sidebar.extra" to stderr and exit with code 0 (warning only, not failure)
