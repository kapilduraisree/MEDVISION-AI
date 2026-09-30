import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // Disable automatic entry scanning (esbuild realpath bug with spaces in path on Windows)
    entries: [],
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'recharts',
              'react-hot-toast', 'react-dropzone', 'react-markdown',
              'date-fns', 'lucide-react'],
    force: false,
  },
  server: {
    port: 3000,
    host: true,
    watch: {
      usePolling: true,
      interval: 1000,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
