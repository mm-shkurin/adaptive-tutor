import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => {
  const env = { ...loadEnv(mode, process.cwd(), ''), ...process.env }
  const port = Number(env.FRONTEND_PORT) || 5173
  const serving = command === 'serve' && !env.VITEST
  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port,
      strictPort: true,
      proxy: serving ? { '/api': { target: proxyTarget(env), changeOrigin: true } } : undefined,
    },
    preview: {
      host: '127.0.0.1',
      port,
      strictPort: true,
    },
    test: {
      environment: 'jsdom',
      env: { TZ: 'Europe/Moscow' },
    },
  }
})

function proxyTarget(env) {
  const target = env.VITE_API_PROXY_TARGET
  if (target) return target
  throw new Error(
    'VITE_API_PROXY_TARGET is unset. Copy frontend/.env.example to frontend/.env and set the backend, for example http://127.0.0.1:8000',
  )
}
