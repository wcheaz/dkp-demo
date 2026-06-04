## 1. Localization Setup

- [x] 1.1 Add translation keys for the 3D viewport control panel and loading overlay to English and Slovak messages.
  - **Done when**: The JSON dictionaries in `src/i18n/messages/en.json` and `src/i18n/messages/sk.json` contain the keys `topView`, `frontView`, `sideView`, `isometricView`, `perspective`, `orthographic`, `resetView`, and `parsingGeometry` under the `designs` section.
  - **Verify by**: Verifying the JSON syntax is valid and `npm run build` compiles successfully.
  - **Stop and hand off if**: A syntax error in either file breaks translation parsing and cannot be recovered.

## 2. Component Integration

- [x] 2.1 Dynamically import the `CadViewer3D` component in `src/components/design-component.tsx`.
  - **Done when**: `CadViewer3D` is imported via Next.js `dynamic()` with `ssr: false` in `src/components/design-component.tsx`.
  - **Verify by**: Verifying that the import statement matches Next.js dynamic syntax guidelines.
  - **Stop and hand off if**: Dynamic import fails to resolve the component path or typescript errors occur.

- [x] 2.2 Replace the 2D CAD viewer with the dynamically imported `CadViewer3D` inside the fullscreen modal view block in `src/components/design-component.tsx`.
  - **Done when**: The JSX elements within the fullscreen view block render `<CadViewer3D>` with the correct `key`, `dxfContent`, and `className` props.
  - **Verify by**: Running typescript check or building the project to confirm there are no JSX compilation errors.
  - **Stop and hand off if**: Type mismatch or layout conflicts occur that break compilation.

- [x] 2.3 Localize `src/components/cad-viewer-3d.tsx` buttons, tooltips, and loading labels.
  - **Done when**: All hardcoded English user-facing strings in `src/components/cad-viewer-3d.tsx` (such as "Top (2D)", "Front", "Side", "Isometric", "Perspective", "Orthographic", "Reset View", and "Parsing 3D Geometry...") are replaced with the `useTranslations("designs")` dictionary hooks.
  - **Verify by**: Verifying that compilation succeeds and checking that no hardcoded English strings remain in the component layout.
  - **Stop and hand off if**: Compilation fails due to `useTranslations` type issues or incorrect translation hooks.

## 3. Agent Skills Compatibility

- [x] 3.1 Update agent skill references to specify 3D-compatible DXF output configurations.
  - **Done when**: The file `.agents/skills/run-generate-design/references/dxf-builder-api.md` is updated to document that the `Dimensions` and `Labels` layers use standard `TEXT` or `MTEXT` labels instead of `DIMENSION` objects, and explicitly documents the exclusion of `DIMENSION` objects to prevent WebGL viewer crashes.
  - **Verify by**: Reviewing the contents of the modified `dxf-builder-api.md` reference file.
  - **Stop and hand off if**: Document edits conflict with existing agent skill validations.
