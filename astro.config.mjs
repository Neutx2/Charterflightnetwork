// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import { DUPLICATE_PATHS } from './src/lib/directory-dupes.ts';

// https://astro.build/config
export default defineConfig({
  site: 'https://charterflightnetwork.com',
  output: 'static',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
  },
  integrations: [
    sitemap({
      // keep the sitemap to canonical, indexable pages: per-operator quote
      // pages canonicalize to /quote, and utility pages add no search value
      filter: (page) =>
        !/\/quote\/.+/.test(page) &&
        !page.endsWith('/quote-confirmation/') &&
        !page.endsWith('/404/') &&
        // duplicate directory twins canonicalize to their primary
        !DUPLICATE_PATHS.some((d) => page.endsWith(d)),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
