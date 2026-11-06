/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_HOTEL_NAME: process.env.NEXT_PUBLIC_HOTEL_NAME || 'Grand Azure Resort & Hotel'
  }
};

module.exports = nextConfig;

