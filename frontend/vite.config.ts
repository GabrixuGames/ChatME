import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "127.0.0.1",
    port: 8080,
    strictPort: true,
    historyApiFallback: true,
    proxy: {
      '/procesar_login': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/register': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/logout': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/verificar_sesion': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/chat': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/friends': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          if (id.includes("react")) return "react";
          if (id.includes("@radix-ui")) return "radix";
          if (id.includes("lucide-react")) return "icons";
          if (id.includes("recharts")) return "charts";
          if (id.includes("@tanstack")) return "tanstack";
          return "vendor";
        },
      },
    },
  },
}));
