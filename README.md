# blog

Astro-powered static blog for `blog.brandoncamenisch.com`.

## Stack

- Astro
- GitHub Actions
- GitHub Pages
- Markdown / MDX content collections

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Deployment

Deployments run through GitHub Actions and publish to GitHub Pages.

Important files:

- `astro.config.mjs` sets `site` to `https://blog.brandoncamenisch.com`
- `public/CNAME` declares the custom domain
- `.github/workflows/deploy.yml` builds and deploys the static site

## Content

Posts live in `src/content/blog/`.
