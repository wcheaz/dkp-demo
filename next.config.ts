import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["@copilotkit/runtime"],
  // Ensure consistent route matching for API routes
  trailingSlash: false,
  // Disable source maps in production for security and performance
  productionBrowserSourceMaps: false,
};

export default nextConfig;
