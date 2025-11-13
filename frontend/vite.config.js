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
    'import.meta.env.VITE_WOMPI_PUBLIC_KEY': JSON.stringify('pub_prod_yG6ag71rCqGUJmVfgrYPSOFQfkjGHXOT'),
    // PayPal client ID
    'import.meta.env.VITE_PAYPAL_CLIENT_ID': JSON.stringify('AfoqONwK05N0j548Xeff7ZdHfg699MJQj79RYRdCaGvN3ZQCA4Yu6ioEHD0zF1vdnLo_2UKaCqrwRAok'),
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
