import { defineConfig } from 'astro/config';
import sitemap from "@astrojs/sitemap";
import mdx from "@astrojs/mdx";
import icon from "astro-icon";

// https://astro.build/config
export default defineConfig({
  site: 'https://www.billgehring.com/', // Public domain — used for canonical URLs and the generated sitemap.
  integrations: [sitemap(), mdx(), icon()],
});