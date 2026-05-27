import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["@copilotkit/runtime"],
  trailingSlash: false,
  productionBrowserSourceMaps: false,
  turbopack: {
    resolveAlias: {
      fs: { browser: "" },
      path: { browser: "" },
    },
  },
};

export default nextConfig;
