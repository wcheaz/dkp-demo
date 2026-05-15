## ADDED Requirements

### Requirement: LanguageToggle component renders in development only
A `LanguageToggle` component SHALL be exported from `src/components/language-toggle.tsx`. When `NODE_ENV === 'development'`, it SHALL render a set of buttons — one per locale in `locales` (`SK`, `EN`). The currently active locale button SHALL be visually distinguished (bold + underline). Clicking a button SHALL call `setLocale` from `useLanguage()`. When `NODE_ENV === 'production'`, the component SHALL return `null`.

#### Scenario: Toggle renders buttons in development
- **WHEN** `LanguageToggle` is rendered during `NODE_ENV=development`
- **THEN** it SHALL render two buttons labeled "SK" and "EN"

#### Scenario: Active locale is visually distinguished
- **WHEN** `LanguageToggle` is rendered and `locale` is `"en"`
- **THEN** the "EN" button SHALL have bold and underline styling, and the "SK" button SHALL NOT

#### Scenario: Clicking button changes locale
- **WHEN** the user clicks the "SK" button
- **THEN** `setLocale("sk")` SHALL be called

#### Scenario: Toggle is hidden in production
- **WHEN** `LanguageToggle` is rendered during `NODE_ENV=production`
- **THEN** the component SHALL return `null` and render no DOM elements

### Requirement: LanguageToggle rendered in page header
`src/app/page.tsx` or `src/app/layout.tsx` SHALL import and render `LanguageToggle` within the page header area, so it is visible at the top of the page in development.

#### Scenario: Toggle appears in page header
- **WHEN** the app is running in development mode
- **THEN** the `LanguageToggle` component SHALL be rendered and visible in the page header area
