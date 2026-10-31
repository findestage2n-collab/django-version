import { fileURLToPath, URL } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [vue(), tailwindcss()],
    resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
    server: {
      port: 5173,
      // En dev, l'API Django est atteinte via le proxy : pas de CORS à gérer.
      proxy: {
        "/api": {
          target: env.VITE_API_PROXY_TARGET ?? "http://localhost:8000",
          changeOrigin: false,
        },
      },
    },
    test: { environment: "jsdom", globals: true, include: ["src/**/*.spec.ts"] },
  };
});
