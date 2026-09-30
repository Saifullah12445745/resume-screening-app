import { defineConfig } from 'vite';
export default defineConfig({define:{'import.meta.env.VITE_VERCEL':JSON.stringify(process.env.VERCEL || '0')},server:{proxy:{'/api':'http://127.0.0.1:8000'}}});
