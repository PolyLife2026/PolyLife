// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/team1/api': {
        target: 'http://localhost:9101',
        changeOrigin: true,
      }
    }
  }
})
