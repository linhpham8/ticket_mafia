import type { NextConfig } from "next";

const apiBaseUrl = process.env.NEXT_PUBLIC_TICKET_MAFIA_API_BASE_URL ?? "http://127.0.0.1:8080";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiBaseUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
