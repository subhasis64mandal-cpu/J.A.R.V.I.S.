import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/events': 'http://127.0.0.1:8787',
      '/state': 'http://127.0.0.1:8787',
      '/command': 'http://127.0.0.1:8787',
    },
  },
})
