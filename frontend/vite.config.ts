import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    // Proxy API requests to the backend
    proxy: {
      "/api": {
        // target: 'http://localhost:5000/',
        target: "http://localhost:5000/",
        changeOrigin: true,
      },
      "/static": {
        target: "http://backend:5000/",
        // target: "http://localhost:5000/",
        changeOrigin: true,
      },
    },
  },
});
