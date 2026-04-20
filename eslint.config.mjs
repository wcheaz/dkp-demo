import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
      ".venv/**",
      "agent/.venv/**",
      "*.min.js",
      "*.min.css",
      "*.log",
      ".env*",
      ".backup/**",
    ],
  },
];

export default eslintConfig;
