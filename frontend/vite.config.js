import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          chart: ['chart.js', 'react-chartjs-2'],
          icons: ['lucide-react']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true
  },
  define: {
    global: 'globalThis'
  }
}) 