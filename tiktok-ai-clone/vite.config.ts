import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    hmr: {
      // Disable WebSocket for HMR
      protocol: 'http',
      // Use polling instead (more reliable in some environments)
      overlay: false,
    },
    // Add CORS headers
    headers: {
      'Access-Control-Allow-Origin': '*',
      // Remove COEP header that's causing issues with external resources
      // 'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Opener-Policy': 'same-origin',
    },
  },
  // Optimize handling of video files
  optimizeDeps: {
    exclude: ['video.js'], // Exclude video.js from optimization if used
  },
  build: {
    // Ensure proper handling of large assets
    assetsInlineLimit: 0, // Don't inline any assets
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
}); 