/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      unstable_enableEarlyTranspilation: true
    }
  }
};

export default nextConfig;
