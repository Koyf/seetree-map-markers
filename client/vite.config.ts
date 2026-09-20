import { defineConfig } from 'vite'

export default defineConfig({
  // One .env at the repo root serves both `npm run dev` and docker compose.
  envDir: '..',
})
