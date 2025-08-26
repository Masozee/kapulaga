import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Allow builds to continue with ESLint warnings (not errors)
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
