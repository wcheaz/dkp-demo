## 1. i18n Infrastructure

- [x] 1.1 Install `next-intl` and create `src/i18n/config.ts` with `locales`, `Locale` type, and environment-based default locale (`en` in dev, `sk` in prod). Verify by running `npm ls next-intl` and checking the config file exports correctly.
  Done when: `npm ls next-intl` shows the package, and `config.ts` exports `locales`, `Locale`, and a default derived from `NODE_ENV`.

- [x] 1.2 Create `src/i18n/messages/en.json` with English translations for all user-facing strings (sidebar, designs, pricing, alerts, metadata). Key structure: nested by component (`sidebar.*`, `designs.*`, `pricing.*`, `alerts.*`, `metadata.*`). Verify by confirming the file is valid JSON with no empty values.
  Done when: `node -e "const m = require('./src/i18n/messages/en.json'); console.log(Object.keys(m).join(','))"` prints section names and all leaf values are non-empty strings.

- [x] 1.3 Create `src/i18n/messages/sk.json` with Slovak translations using identical key structure to `en.json`. Slovak domain terms from the planning doc (väzník, pôdorys, rímsa, previs, etc.) MUST be used for domain vocabulary. Verify by confirming valid JSON and matching keys.
  Done when: `node -e "const m = require('./src/i18n/messages/sk.json'); console.log(Object.keys(m).join(','))"` prints the same section names as `en.json`, and domain terms like "väzník" appear in values.

- [x] 1.4 Create `src/i18n/language-provider.tsx` with `LanguageProvider` component and `useLanguage` hook. Provider reads `localStorage('locale')` on mount, falls back to `data-default-locale` HTML attribute, exposes `locale`, `setLocale`, `isDevelopment`. `setLocale` persists to localStorage and sets `document.documentElement.lang`. Verify by rendering the provider in a test component and checking locale state changes.
  Done when: The file exports `LanguageProvider` and `useLanguage`, calling `setLocale('sk')` updates `localStorage.getItem('locale')` to `"sk"` and `document.documentElement.lang` to `"sk"`.

- [x] 1.5 Create `scripts/check-i18n-parity.mjs` that flattens and compares keys between `en.json` and `sk.json`. Missing keys in `sk.json` = exit 1. Add `"i18n:check": "node scripts/check-i18n-parity.mjs"` to `package.json` scripts. Verify by running `npm run i18n:check` — it should exit 0 with both complete dictionaries.
  Done when: `npm run i18n:check` exits 0. Temporarily remove a key from `sk.json` and confirm it exits 1 with an error message, then restore the key.

## 2. Language Toggle Component

- [x] 2.1 Create `src/components/language-toggle.tsx` with `LanguageToggle` component. Renders EN/SK buttons in development, returns `null` in production. Uses `useLanguage()` hook. Active locale gets bold + underline. Verify by rendering in dev mode (shows buttons) and confirming production mode returns null.
  Done when: Component renders two buttons in dev, returns `null` in production, and clicking a button calls `setLocale`.

- [x] 2.2 Integrate `LanguageToggle` into the page header. Add to `src/app/page.tsx` or `src/app/layout.tsx` in the header area so it is visible at the top in development. Verify by running `npm run dev` and confirming the toggle appears in the header.
  Done when: `npm run dev` shows EN/SK toggle in the page header area. `npm run build && npm start` does NOT show the toggle.

## 3. Layout and Metadata

- [x] 3.1 Update `src/app/layout.tsx`: set `<html lang>` dynamically based on locale (default `"sk"` for Slovak). Set `data-default-locale` attribute on `<html>` to `"sk"` or `"en"` based on `NODE_ENV`. Replace hardcoded metadata title/description with Slovak values from translation dictionary. Wrap app with `LanguageProvider`. Verify by checking `<html lang="sk">` in production and `<html lang="en">` in dev (default).
  Done when: `<html>` element has `data-default-locale` attribute, `lang` attribute updates when locale changes, and metadata uses translated values.

## 4. Migrate Frontend Components to useTranslations

- [x] 4.1 Migrate `src/app/page.tsx` — replace all hardcoded user-facing strings with `useTranslations()` calls. This includes: sidebar title (`sidebar.title`), greeting (`sidebar.greeting`), placeholder (`sidebar.placeholder`), suggestion titles and messages (`sidebar.suggestions.*`), file upload alert messages (`alerts.*`), CustomInput placeholder text. Tool descriptions and parameter descriptions stay in English (LLM-facing). Verify by running `npm run dev`, confirming the app renders correctly in English (dev default), then toggling to Slovak and confirming all user-visible text changes.
  Done when: All user-visible text in `page.tsx` comes from translation keys. Hardcoded English strings like `"Design Assistant"`, `"Type a message..."`, `"Generate a sample design"` no longer appear in the source as bare strings. `npm run dev` renders correctly in both locales.

- [x] 4.2 Migrate `src/components/design-component.tsx` — replace `MATERIAL_STAT_LABELS` and `PARAM_LABELS` objects with translated values from `useTranslations('designs')`. Replace heading `"Designs"`, empty state text, `"Generating truss structure..."`, `"Material Estimate"`, `"Price:"`, `"Design In Progress"` alt text, and currency symbol with translation keys. Switch number formatting to `Intl.NumberFormat('sk-SK')`. Verify by rendering designs in both English and Slovak locales.
  Done when: The hardcoded English label objects are removed. All label text comes from translation keys. `npm run dev` shows translated labels when toggled to Slovak. Currency formatting uses Slovak locale.

- [x] 4.3 Migrate `src/components/pricing-breakdown-modal.tsx` — replace all row labels, tooltips, modal title, fallback message, "Stored price:" label, "(excl. VAT)" suffix, and "Unknown" fallback with translation keys from `useTranslations('pricing')`. Switch `toLocaleString("en-US")` to `Intl.NumberFormat('sk-SK')`. Verify by opening the pricing modal in both locales.
  Done when: All hardcoded English strings in the modal are replaced. `toLocaleString("en-US")` no longer appears. Pricing modal displays correctly in both English and Slovak.

- [x] 4.4 Migrate `src/components/add-design-button.tsx` — replace `"Add Test Design"` button label and `"Test design #N"` text with translation keys. Verify by clicking the button in both locales.
  Done when: Button label changes when toggling locale. The `#N` counter still works correctly.

## 5. Agent Locale Awareness

- [x] 5.1 Refactor `agent/src/agent.py` — extract the system prompt into a function `get_system_prompt(locale: str = "sk") -> str` that appends a language instruction based on locale (`"sk"` → "Respond in Slovak", `"en"` → "Respond in English", default → Slovak). Update the agent instantiation to call this function. The base prompt content remains unchanged. Verify by running `cd agent && python -m ruff check . && python -m mypy .` — both must exit 0.
  Done when: `get_system_prompt("sk")` returns a string containing "Slovak", `get_system_prompt("en")` returns a string containing "English". `ruff check` and `mypy` both pass.

- [x] 5.2 Forward frontend locale to the agent via CopilotKit context. The frontend's current locale (from `useLanguage()`) SHALL be passed to the backend agent so `get_system_prompt` receives the correct locale. Add the locale to the CopilotKit readable context or agent state. Verify by sending a message with locale "en" (agent responds in English) then toggling to "sk" (agent responds in Slovak).
  Done when: The agent's response language matches the frontend's current locale setting. English prompts in English locale produce English responses. Slovak locale produces Slovak responses.

## 6. Fix Language Toggle Crash (Regression)

- [x] 6.1 Remove duplicate `LanguageProvider` from `page.tsx`. The provider already exists in `layout.tsx` wrapping the entire app. The second provider in `page.tsx` (lines 29-35) creates a disconnected state — when the toggle updates one provider, the other doesn't know. Remove the `LanguageProvider` wrapper from `CopilotKitPage()` in `page.tsx` and remove the unused import. The page components should use the single provider from `layout.tsx`.
  Done when: `LanguageProvider` appears only in `layout.tsx`, not in `page.tsx`. The toggle and all page components share the same context instance.

- [x] 6.2 Memoize `CopilotSidebar` props (`labels` and `suggestions`) to prevent CopilotKit re-initialization on locale change. The `labels` object and `suggestions` array are created inline on every render, producing new references each time. When locale changes, CopilotKit receives new `labels.initial` and `suggestions`, which causes it to reinitialize its internal chat state and crash. Wrap them with `useMemo` keyed on locale so they only update when the locale actually changes.
  Done when: `labels` and `suggestions` are wrapped in `useMemo(() => {...}, [locale])`. Clicking the language toggle no longer crashes the app. The sidebar title and suggestions update to the new language without resetting chat state.

- [x] 6.3 Fix the `setState` call in the locale sync `useEffect` (page.tsx ~line 350-354). Calling `setState` from `useCoAgent` on every locale change triggers CopilotKit to re-sync agent state with the backend, which can destabilize the connection. Move the locale-to-agent-state sync into the `useCopilotReadable` value so the locale is passed as context without triggering a state mutation.
  Done when: The `useEffect` that calls `setState` on locale change is removed or replaced with a non-mutating approach. The locale is still available to the agent via `useCopilotReadable` without triggering CopilotKit re-sync. Toggle still works without crash.

- [ ] 6.4 Verify language toggle works without crashing. Start dev server, load page, click EN, click SK, click EN again. Confirm: no crash, sidebar updates language, suggestions update, chat history persists, design component re-renders with translated labels. Check browser console for errors.
  Done when: Repeatedly toggling between EN and SK does not crash the app. Console shows no errors. Chat history is preserved across toggles.

## 7. Verification and Quality Gates

- [ ] 7.1 Run `npm run i18n:check` and confirm both dictionaries have identical key structures. Run `npm run build` and confirm no TypeScript errors from translation key references. Run `npm run lint` and confirm no lint errors. Verify by running all three commands and confirming they exit 0.
  Done when: `npm run i18n:check`, `npm run build`, and `npm run lint` all exit 0.

- [ ] 7.2 Visual parity check in development — run `npm run dev`, test in English (default), then toggle to Slovak. Verify: all labels/buttons/headings display in Slovak, no English bleed-through, no layout overflow from longer Slovak text, suggestion buttons wrap correctly, number formatting uses Slovak locale. Run `npm run build && npm start` and confirm the toggle is hidden and Slovak is the default.
  Done when: Both locales render cleanly. No missing translation keys (no raw key paths visible). Slovak text fits within all containers. Production build shows Slovak by default with no toggle.
