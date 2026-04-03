import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // server: {
  //   https: {
  //     key: fs.readFileSync(path.resolve(__dirname, '../ssl/key.pem')),
  //     cert: fs.readFileSync(path.resolve(__dirname, '../ssl/cert.pem')),
  //   },
  //   port: 5173,
  //   host: true,
  //   proxy: {
  //     '/admin': {
  //       target: 'https://localhost:8000',
  //       changeOrigin: true,
  //       secure: false,
  //       ws: true,
  //       cookieDomainRewrite: 'localhost',
  //     },
  //     '/api': {
  //       target: 'https://localhost:8000',
  //       changeOrigin: true,
  //       secure: false,
  //       cookieDomainRewrite: 'localhost',
  //     },
  //     '/static': {
  //       target: 'https://localhost:8000',
  //       changeOrigin: true,
  //       secure: false,
  //       cookieDomainRewrite: 'localhost',
  //     },
  //   },
  // },
  server: {
    port: 5173,
    host: true,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
  },
})
