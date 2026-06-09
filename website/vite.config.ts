import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  cacheDir: "/tmp/ticket-mafia-vite-playwright",
  plugins: [react()]
});
