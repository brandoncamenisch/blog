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
eval "$HOME/.password-store/scripts/export-pass-env.sh haxor/cloudflare/blog-tofu"

./scripts/tofu-docker.sh plan
./scripts/tofu-docker.sh apply -auto-approve
```

This configuration manages the `blog` CNAME pointing at
`brandoncamenisch.github.io`.

For pipeline usage, configure these GitHub Actions secrets:

- `CLOUDFLARE_API_TOKEN`
- `TF_VAR_CLOUDFLARE_ZONE_ID`

Then use the manual workflow:

- `.github/workflows/cloudflare-tofu.yml`

That workflow runs the same Dockerized OpenTofu path as local usage.

## Content

Posts live in `src/content/blog/`.
