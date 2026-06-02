/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produce a self-contained server bundle for a slim Docker image.
  output: "standalone",
};

module.exports = nextConfig;
