import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from "@tailwindcss/vite"
import Icons from "unplugin-icons/vite";

export default defineConfig({
  plugins: [
    sveltekit(), 
    tailwindcss(), 
    Icons({ compiler: 'svelte', autoInstall: true })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/echarts')) {
            return 'echarts';
          }
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    },
    // chunkSizeWarningLimit: 600
  },
  server: {
    port: 5173,
    open: true
  }
});