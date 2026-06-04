# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Bill Gehring's personal/academic website (https://www.billgehring.com), a static
site built with **Astro 4**. It started from the [Odyssey theme](https://odyssey-theme.sapling.supply)
(`treefarmstudio/odyssey-theme`), so a fair amount of theme scaffolding (demo
components, landing-page/blog/company routes, Firebase config) is still present
but unused. Most real changes are content edits, not feature code.

## Commands

```bash
npm run dev      # astro dev — local dev server with HMR
npm run build    # astro build — outputs static site to dist/
npm run preview  # astro preview — serve the built dist/ locally
npm run format   # prettier -w . (uses prettier-plugin-astro)
```

There is no test suite and no linter beyond Prettier.

## Editing content (the common task)

- **Page text** lives in Markdown at `src/pages/<section>/index.md` (e.g.
  `about`, `teaching`, `publications`, `research`, `contact`). Each file's
  frontmatter sets `layout: ../../layouts/MarkDownPage.astro` and the body is
  plain Markdown (raw HTML like `<hr>` is allowed). The home page is
  `src/pages/index.astro`.
- **Navigation** is data-driven in `src/config/nav.js` (title → page slug). Edit
  this to add/remove/reorder header links — do not hardcode nav in layouts.
- **PDFs and downloads** (CV, resume, ~80 published paper PDFs, an NPR audio
  clip) live in `public/files/` and are served at `/files/...`. To update the
  CV or resume, replace `public/files/BillGehring_CV_Latest.pdf` /
  `BillGehring_Resume_Latest.pdf` (the publications page links these by name).

## Architecture

**Layout chain** (each wraps the next via `<slot />`):
`Base.astro` (html/head/body + `BaseHead`) → `Page.astro` (adds `Header`,
`Footer`, and nav from config) → `MarkDownPage.astro` (wraps Markdown content in
a narrow `Container` + `<article>`). Markdown pages get `Page.astro`'s chrome
automatically through `MarkDownPage`.

**Component barrel.** Shared components are re-exported from
`src/components/odyssey-theme.js` and imported as
`import { Container, Header, Footer } from '@components/odyssey-theme'`. Prefer
this barrel over deep relative paths.

**Path aliases** (defined in `tsconfig.json`, `baseUrl: src`): `@components/*`,
`@config`, `@layouts/*`, `@styles/*`, `@utils/*`, `@icons`, `@assets/*`,
`@pages/*`.

**Astro integrations** (`astro.config.mjs`): `sitemap`, `mdx`, `lit`,
`astro-icon`. `site` is set to the production domain for canonical URLs/sitemap.

**Site-wide config** is centralized in `src/config/`: `settings.js`
(title/url/name, theme-switcher toggle), `nav.js`, `footer.js`. Note: `footer.js`
still contains the theme's demo links (Landing Pages, Theme, Company) — only
`nav.js` reflects the real site.

## Styling

Global CSS is imported **once**, in `src/components/head/BaseHead.astro`, via
`src/styles/index.css`, which `@import`s in order: `reset.css` → `theme.css` →
`typography.css` → `global.css`.

- Theme tokens are CSS custom properties (`--theme-primary`, `--theme-surface-1`,
  `--section-margin`, etc.) defined in `src/styles/theme.css`. Components style
  against these variables — change the look here rather than per-component.
- **Active typography is `src/styles/typography.css`.** The sibling files
  `typography copy 2.css`, `typography orig.css`, and `typography_extra2.css` are
  unused backups — do not edit them expecting changes to appear.
- Fonts (Lato, Roboto Serif) are self-hosted as woff/woff2 in `src/fonts/` and
  `public/assets/fonts/`.

## Deployment

The live site deploys via **Netlify** (`netlify.toml`: `command = npm run build`,
`publish = dist/`). `dist/` is the build output and is gitignored.

`firebase.json` / `.firebaserc` are leftovers from the upstream Odyssey theme
(site `odyssey-theme-sapling`, project `sapling-supply`) and are **not** the
deploy target for this site — ignore them unless intentionally switching hosts.
