/** @type {import('next').NextConfig} */
const devToolsUrl = process.env.DEV_TOOLS_URL || 'http://localhost:8090'

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/dev-tools/:path*',
        destination: `${devToolsUrl}/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
        ],
      },
    ];
  },
};
module.exports = nextConfig;
