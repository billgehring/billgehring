# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Bill Gehring's personal/academic website (https://www.billgehring.com), a static
site built with **Astro 6**. It started from the [Odyssey theme](https://odyssey-theme.sapling.supply)
(`treefarmstudio/odyssey-theme`), so some theme scaffolding (demo components,
landing-page/blog/company routes) is still present but unused. Most real changes
are content edits, not feature code.

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
  `about`, `teaching`, `research`, `contact`). Each file's
  frontmatter sets `layout: ../../layouts/MarkDownPage.astro` and the body is
  plain Markdown (raw HTML like `<hr>` is allowed). The home page is
  `src/pages/index.astro`.
- **Publications** are data, not Markdown: `cv/publications.yaml` is the single
  source of truth shared by the website and the CV (field docs at the top of the
  file; newest first). `src/content.config.ts` loads it as the `publications`
  content collection with a strict schema (a typo'd field fails the build), and
  `src/components/Publications.astro` renders APA citations with `[doi]`/`[PDF]`
  links for `src/pages/publications/index.astro`. Add a paper = add one YAML
  entry (+ drop its PDF in `public/files/`). `pdf:` holds the bare filename;
  the site links it as `/files/<name>`, the CV as
  `https://billgehring.com/files/<url-encoded name>`.
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

**Astro integrations** (`astro.config.mjs`): `sitemap`, `mdx`, `astro-icon`.
`site` is set to the production domain for canonical URLs/sitemap.

**Site-wide config** is centralized in `src/config/`: `settings.js`
(title/url/name), `nav.js`, `footer.js`. Note: `footer.js` still contains the
theme's demo `footerLists` (Landing Pages, Theme, Company), but `Footer.astro`
never renders them — only `footerSocials` (the social icons) and `nav.js` reach
the page.

## Styling

Global CSS is imported **once**, in `src/components/head/BaseHead.astro`, via
`src/styles/index.css`, which `@import`s in order: `reset.css` → `theme.css` →
`typography.css` → `global.css`.

- Theme tokens are CSS custom properties (`--theme-primary`, `--theme-surface-1`,
  `--section-margin`, etc.) defined in `src/styles/theme.css`. Components style
  against these variables — change the look here rather than per-component.
- **Typography lives in `src/styles/typography.css`** (the only typography file;
  old backup copies were removed).
- Display fonts are pulled via `@import` at the top of `typography.css` (Typekit
  + Google Fonts — Merriweather for headings, source-sans-pro for body). Some
  self-hosted woff/woff2 files remain in `src/fonts/` and `public/assets/fonts/`
  but appear to be leftover and unused.

## Deployment

The live site is hosted on **a2hosting / hosting.com** (chosen for its detailed
visitor logs), in a shared `public_html` that also serves six other
sites/subdomains plus some old projects — so any deploy must **only add/update
this site's files and never delete**.

**Automated (default):** pushing to `main` triggers
`.github/workflows/deploy.yml`, which builds the site and `rsync`s `dist/` into
`public_html` over SSH **without `--delete`**. Publishing is just `git push`;
you can also re-run it from the repo's **Actions** tab ("Run workflow"). Auth is
four repository secrets (`A2_SSH_HOST`, `A2_SSH_USER`, `A2_SSH_PORT`,
`A2_SSH_KEY`) — the deploy key's public half is authorized in cPanel, its
private half is the `A2_SSH_KEY` secret. `dist/` is gitignored (built in CI).
Trade-off of no `--delete`: a page removed from the repo lingers on the server
until you delete it there by hand. **Never add `--delete`** — it would wipe the
co-hosted sites. Verify scope with `rsync -n` before changing deploy behavior.

**Manual fallback:** `npm run build`, then upload the contents of `dist/` into
`public_html` via cPanel — do not clear the directory first; other sites live
there.

## Visitor & security diagnostics

Goal: spot malicious actors (vulnerability scanners, scrapers, brute-force
probes). **Key fact: attackers and bots almost never run JavaScript**, so
client-side analytics (Google Analytics, Plausible, etc.) cannot see them. The
security signal lives in **server access logs** and at the **network edge**.
This is a runbook to set up and revisit later — none of it is wired into the
site code yet.

**What you already have** (a2hosting cPanel → "Metrics"): raw Apache access
logs plus AWStats/Webalizer. Every request is already recorded (IP, time, path,
status code, user-agent, referrer). The steps below make that data usable and
add active defense.

### 1. GoAccess — turn raw logs into a readable dashboard (free, runs locally)

Best first step; no server install and no DNS changes.

1. cPanel → Metrics → **Raw Access** → download the log (often gzipped). If so:
   `gunzip access.log.gz`
2. Install once on your Mac: `brew install goaccess`
3. Generate a report: `goaccess access.log --log-format=COMBINED -o report.html`
   then open `report.html` in a browser.
4. **Red flags to look for:** repeated hits to paths the site doesn't have
   (`/wp-login.php`, `/.env`, `/xmlrpc.php`, `/.git/`, `/phpmyadmin`); bursts of
   404/403/500 responses; a single IP with abnormally high request volume; odd
   user-agents; unexpected countries. Those are almost always probes/scanners.

### 2. Cloudflare — active protection + threat dashboard (free tier)

GoAccess only *observes*. Cloudflare sits in front of the site and can *block*
bad traffic before it ever reaches a2hosting.

1. Free account at cloudflare.com → **Add a site** → `billgehring.com`.
   Cloudflare scans existing DNS and gives you two nameservers.
2. At the domain registrar, replace the current nameservers with Cloudflare's.
   (Propagation takes minutes–hours; the site stays up the whole time.)
3. Make sure the site's DNS record is **Proxied** (orange cloud) so traffic
   actually routes through Cloudflare.
4. Enable protection: Security → Bots → **Bot Fight Mode**; Security → WAF →
   turn on the free managed ruleset; optionally add a **Rate Limiting** rule.
5. Watch: **Security → Events** shows what was challenged/blocked; **Analytics**
   shows traffic, threats, and country breakdown.
6. **Keep your logs useful:** once proxied, a2hosting will log Cloudflare's IPs
   instead of real visitors. Cloudflare passes the true IP in the
   `CF-Connecting-IP` header — ask a2hosting support to enable `mod_remoteip`
   (a.k.a. "restore visitor IP") so access logs and GoAccess reports show real
   client IPs again.

**Does Cloudflare challenge every visitor?** No. It scores each request (IP
reputation, fingerprint, behavior) first and only challenges traffic that looks
suspicious. Modern challenges are mostly **invisible "Managed Challenges"** — a
brief background check, not the old click-the-images CAPTCHA — so normal human
visitors typically see nothing. Verified search crawlers (Googlebot, Bingbot)
are allowlisted, so indexing and Google Scholar are unaffected. The full-page
"Checking your browser…" interstitial shown to *everyone* appears only if you
enable **"Under Attack Mode"** (an emergency switch for an active DDoS) — leave
it off for normal operation.

### 3. (Optional) Clean human-visitor metrics

For "how many real people visited" numbers, add a privacy-friendly, cookie-less
tracker: **Cloudflare Web Analytics** (free; no separate signup if already on
Cloudflare) or self-hosted **Umami**. These *miss* bots by design, so they
complement — not replace — items 1 & 2. Note: adding any client tracker
reintroduces JavaScript to what is currently a zero-JS site.

**Priority for the malicious-actor goal:** GoAccess first (immediate, free, no
DNS change), then Cloudflare (ongoing active defense).
