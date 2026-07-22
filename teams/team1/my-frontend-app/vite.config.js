// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // Backend is exposed via the team gateway (default TEAM_PORT=9101), not port 8000.
  const apiTarget = env.VITE_API_PROXY || 'http://localhost:9101'

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/team1/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
