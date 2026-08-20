import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  // Configuración para build con cache busting
  build: {
    outDir: '../backend/static/frontend',
    emptyOutDir: true,
    manifest: true, // Genera manifest.json para mapear archivos con hash
    rollupOptions: {
      output: {
        // Genera archivos JS con hash en el nombre
        entryFileNames: 'assets/[name].[hash].js',
        // Genera archivos CSS con hash en el nombre
        chunkFileNames: 'assets/[name].[hash].js',
        // Genera otros assets (imágenes, fuentes) con hash
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'assets/[name].[hash].css'
          }
          return 'assets/[name].[hash].[ext]'
        }
      }
    }
  },
  
  // Base URL para los assets en producción
  base: command === 'serve' ? '/' : '/static/frontend/',
  
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: backendUrl,
        changeOrigin: true,
        secure: false,
      },
    },
  },
}))
