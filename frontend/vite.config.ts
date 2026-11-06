/// <reference types="vitest/config" />
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { host: "127.0.0.1", port: 5173, strictPort: true },
  // Preparado para o Tauri: caminhos relativos no build.
  base: "./",
  build: {
    target: "es2022",
    sourcemap: true,
    rollupOptions: { output: { manualChunks: { charts: ["recharts"] } } },
  },
  test: { environment: "jsdom", globals: false },
});
