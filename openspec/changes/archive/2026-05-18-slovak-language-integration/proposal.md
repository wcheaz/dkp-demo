## Why

The application serves Slovak-speaking end users who work with roof truss (väzník) designs. All original domain documents and terminology are Slovak — they were translated to English for developer convenience. Currently every user-facing string is hardcoded English, making the app unusable for its target audience. Slovak MUST be the default in production; English remains the development default so the developer (who does not speak Slovak) can test features.

## What Changes

- Add `next-intl` as the i18n library and configure it for client-side locale switching (no route segments — this is a single-page app with no SEO requirement).
- Create two translation dictionaries (`en.json`, `sk.json`) covering every user-facing string in the UI (~100 strings across 5 files).
- Add a `LanguageProvider` React context that stores the active locale in `localStorage` and derives the default from `NODE_ENV`: English in development, Slovak in production.
- Add a dev-only EN/SK toggle component that renders in `NODE_ENV=development` and returns `null` in production.
- Replace all hardcoded English strings in `page.tsx`, `design-component.tsx`, `pricing-breakdown-modal.tsx`, `add-design-button.tsx`, and `layout.tsx` with `useTranslations()` calls.
- Switch number/currency formatting to Slovak locale (`sk-SK`).
- Make the Python agent's system prompt locale-aware: append a language instruction ("Respond in Slovak" / "Respond in English") based on a locale value forwarded from the frontend through CopilotKit context.
- Create a parity-check script (`scripts/check-i18n-parity.mjs`) that validates `en.json` and `sk.json` have identical key structures, failing CI on mismatch.

## Capabilities

### New Capabilities
- `i18n-infrastructure`: next-intl setup, translation dictionaries, LanguageProvider context, locale config with environment-based defaults, and i18n parity check script.
- `language-toggle`: Dev-only EN/SK toggle component, hidden in production, persisted in localStorage.
- `agent-locale`: Locale-aware agent system prompt that adapts language instruction based on frontend-passed locale via CopilotKit context.

### Modified Capabilities
- `design-display`: All hardcoded English labels (MATERIAL_STAT_LABELS, PARAM_LABELS, headings, empty state, processing text, price label) replaced with translated keys. Currency display switched from GBP to EUR with Slovak locale formatting.
- `pricing-breakdown-modal`: All hardcoded English row labels, tooltips, fallback messages, and stored price label replaced with translated keys. Number formatting switched to `sk-SK` locale.
- `agent-system-prompt`: System prompt becomes locale-aware, appending language instruction dynamically instead of being static English.

## Impact

- **Dependencies**: Add `next-intl` npm package.
- **Frontend files**: `layout.tsx`, `page.tsx`, `design-component.tsx`, `pricing-breakdown-modal.tsx`, `add-design-button.tsx` — all modified to use translation hooks.
- **New files**: `src/i18n/config.ts`, `src/i18n/language-provider.tsx`, `src/i18n/messages/en.json`, `src/i18n/messages/sk.json`, `src/components/language-toggle.tsx`, `scripts/check-i18n-parity.mjs`.
- **Backend files**: `agent/src/agent.py` — system prompt generation becomes a function accepting locale; CopilotKit context forwarding.
- **No breaking changes**: Existing behavior in development (English) is preserved. Production gets Slovak defaults.
- **Tool descriptions and names stay in English**: These are LLM-facing instructions, not user-visible. No translation needed.

## Non-goals

- Route-based locale switching (`/en/...`, `/sk/...`) — not needed for a single-page internal tool.
- SEO or server-rendered locale negotiation.
- Translating the agent's tool names or tool parameter descriptions — these are LLM-internal.
- Native Slovak speaker review of translation quality — that is a human handoff item outside the autonomous loop.
- Currency conversion from CZK/GBP to EUR — the pricing formula stays as-is; only the display formatting changes.
- Translating deployment scripts, CI config, or developer-facing comments.
- Supporting additional languages beyond English and Slovak.
