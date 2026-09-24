import viteCompression from 'vite-plugin-compression'
import vue from '@vitejs/plugin-vue'
import vuetify, {transformAssetUrls} from 'vite-plugin-vuetify'
import {defineConfig} from 'vite'
import {URL, fileURLToPath} from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern'
      }
    }
  },
  define: {'process.env': {}},
  plugins: [
    viteCompression(),
    vue({
      template: {transformAssetUrls}
    }),
    vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/styles/settings.scss'
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue'
    ]
  },
  server: {
    // A leading '.' matches the domain and all of its subdomains, e.g. "pahma.localhost". See
    // the "Working with tenants locally" section of README.md.
    allowedHosts: ['.localhost'],
    port: 8080
  }
})
