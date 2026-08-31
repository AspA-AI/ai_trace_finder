/** @type {import('next').NextConfig} */
const nextConfig = (phase, { defaultConfig }) => ({
  // Keep dev and production artifacts separate. Sharing `.next` lets a
  // production build replace chunks that a long-running dev server still
  // references, which causes intermittent missing-module errors.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
  reactStrictMode: true,
  webpack(config, { dev }) {
    // The development server is long-lived and may be restarted after a
    // move/build. Avoid stale filesystem packs causing missing route chunks.
    if (dev) config.cache = false;
    return config;
  },
});

export default nextConfig;
