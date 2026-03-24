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

## Cloudflare DNS with OpenTofu

The repo includes public-safe OpenTofu config in `infra/cloudflare/` for the
`blog.brandoncamenisch.com` DNS record.

Nothing secret is committed:

- the Cloudflare API token is supplied via `CLOUDFLARE_API_TOKEN`
- the zone ID is supplied via `TF_VAR_cloudflare_zone_id`
- local state and `.tfvars` files are ignored by Git
- no backend config is committed in this public repo

Example local usage:

```bash
export CLOUDFLARE_API_TOKEN=...
export TF_VAR_cloudflare_zone_id=...

cd infra/cloudflare
tofu init
tofu plan
tofu apply
```

This configuration manages the `blog` CNAME pointing at
`brandoncamenisch.github.io`.

## Content

Posts live in `src/content/blog/`.
