import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
  // Docker에서 실행할 때 필요한 설정
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
  // 도커 환경에서 호스트 바인딩
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://gateway:8080/api/:path*',
      },
    ];
  },
};

export default nextConfig;
