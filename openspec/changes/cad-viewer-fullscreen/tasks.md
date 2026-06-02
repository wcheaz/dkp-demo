## 1. Setup & Translations

- [x] 1.1 Add translation keys to `src/i18n/messages/en.json` and `src/i18n/messages/sk.json` for back button (`designs.back`), the fullscreen view title (`designs.fullscreenTitle`), and magnifying glass tooltip (`designs.viewFullscreen`).
  - **Done when**: Both files contain the new keys. Verify with: `grep -cE 'back|fullscreenTitle|viewFullscreen' src/i18n/messages/en.json` returning at least 3 matches, and `grep -cE 'back|fullscreenTitle|viewFullscreen' src/i18n/messages/sk.json` returning at least 3 matches.
  - **Stop and hand off if**: JSON parsing error occurs in either file, or the files are missing.

## 2. Fullscreen State and Layout Integration

- [x] 2.1 Add the `fullscreenDxf` and `fullscreenDesignId` states to `DesignComponent` in `src/components/design-component.tsx`. When `fullscreenDxf` is active, conditionally render the maximized container (`w-full h-[80vh] flex flex-col bg-[#1e1e1e] rounded-2xl border border-gray-700 overflow-hidden relative`) instead of the default designs heading and list. The header of this view must contain the localized title and a "Back" button that resets the states when clicked.
  - **Done when**: The component conditionally renders the fullscreen container when `fullscreenDxf` is not null. Verify with: `grep -cE 'fullscreenDxf|fullscreenDesignId|rounded-2xl bg-\[#1e1e1e\]' src/components/design-component.tsx` returning at least 3 matches.
  - **Stop and hand off if**: TypeScript compile errors or syntax errors occur in `design-component.tsx`.

- [x] 2.2 Inside the fullscreen container of `DesignComponent`, render the `<CadViewer>` component with `key={fullscreenDesignId}`, `dxfContent={fullscreenDxf}`, and class `w-full h-full absolute inset-0` to fill the content area.
  - **Done when**: The `<CadViewer>` is correctly wired inside the fullscreen container block. Verify with: `grep -A 5 'CadViewer' src/components/design-component.tsx` in the conditional fullscreen render block shows `dxfContent={fullscreenDxf}` and `className="w-full h-full absolute inset-0"`.
  - **Stop and hand off if**: Import issues or component typing mismatches arise.

## 3. Magnifying Glass Button on Card Preview

- [ ] 3.1 Wrap the default card-level `CadViewer` inside a `relative w-full h-[27vh]` wrapper, and add an absolute-positioned magnifying glass button (`absolute top-2 right-2 z-10 p-1.5 rounded-lg bg-black/60 hover:bg-black/80 text-gray-300 hover:text-white transition-colors`) that sets the fullscreen state variables on click. The button must use a zoom-in magnifying glass icon (magnifying glass with a plus sign).
  - **Done when**: The relative wrapper and the button with click handler are added to `src/components/design-component.tsx`. Verify with: `grep -c 'absolute top-2 right-2 z-10' src/components/design-component.tsx` returning at least 1 match.
  - **Stop and hand off if**: The layout breaks or positioning offsets the zoom button outside the card boundary.

## 4. Verification and UI Polish

- [ ] 4.1 Run the build command to ensure there are no compilation or type check errors across the project.
  - **Done when**: The `npm run build` command runs successfully with exit code 0. Verify with: running `npm run build` exits with code 0.
  - **Stop and hand off if**: The build fails due to typescript errors, package mismatches, or missing files.
