import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  define: {
    'import.meta.env.VITE_PAYPAL_CLIENT_ID': JSON.stringify(process.env.VITE_PAYPAL_CLIENT_ID || 'AXOC4gQsXk_e8NhrrZRorJzU3rld7lOJP5_2S8RYDKUgjkDT-2wfc-1Eu1AqYQseWTcJA_VBEnGUUGCQ'),
    'import.meta.env.VITE_WOMPI_PUBLIC_KEY': JSON.stringify(process.env.VITE_WOMPI_PUBLIC_KEY || 'pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR'),
  },
  
  // Configuración para build
  build: {
    outDir: '../backend/static/frontend',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'index.css'
          }
          return assetInfo.name
        }
      }
    }
  },
  
  // Base URL para los assets en producción
  base: '/static/frontend/',
  
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
