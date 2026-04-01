// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';
import { remarkGeneratedArticleImages } from './src/utils/generatedArticleImages.mjs';

export default defineConfig({
  site: 'https://brandoncamenisch.com',
  integrations: [mdx(), sitemap()],
  markdown: {
    remarkPlugins: [remarkGeneratedArticleImages],
  },
});
