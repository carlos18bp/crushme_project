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
    // Wompi public key
    'import.meta.env.VITE_WOMPI_PUBLIC_KEY': JSON.stringify('pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR'),
    // PayPal client ID
    'import.meta.env.VITE_PAYPAL_CLIENT_ID': JSON.stringify('AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok'),
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
