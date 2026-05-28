import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["@copilotkit/runtime"],
  trailingSlash: false,
  productionBrowserSourceMaps: false,
  turbopack: {
    resolveAlias: {
      fs: { browser: "./src/lib/empty-module.js" },
      path: { browser: "./src/lib/empty-module.js" },
    },
  },
};

export default nextConfig;
