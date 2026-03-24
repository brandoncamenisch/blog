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

## ComfyUI site imagery

The site ships generated images as static assets committed under
`public/images/generated/`. They are not generated at page load.

Instead, the blog repo includes a Dockerized ComfyUI pipeline that regenerates
those assets before commit when the staged source pages that use them change.

Tracked pieces:

- `comfyui/` contains the Docker build, model-path config, and prompt manifest
- `comfyui/docker-compose.yml` also defines a local Ollama service for prompt synthesis
- `scripts/comfyui-site-images.sh` starts ComfyUI and renders site art
- `scripts/comfyui-site-images.py` reads surrounding page/theme context, asks Ollama for a
  theme-consistent prompt, submits the ComfyUI graph, and copies outputs into
  `public/images/generated/`
- `.githooks/pre-commit` regenerates affected images and re-stages them

One-time setup:

```bash
./scripts/comfyui-site-images.sh install-hooks
```

Place a compatible checkpoint in:

```bash
comfyui/models/checkpoints/
```

The ComfyUI container is configured to request GPU access, so local Docker needs
working NVIDIA runtime support when you want real image generation speed.

The default prompt manifest expects `sd_xl_base_1.0.safetensors`, but you can
change that in `comfyui/site-images.json`.

Pull the Ollama prompt model once:

```bash
./scripts/comfyui-site-images.sh pull-ollama-model
```

Manual usage:

```bash
./scripts/comfyui-site-images.sh preflight landing
./scripts/comfyui-site-images.sh preflight-staged
./scripts/comfyui-site-images.sh up
./scripts/comfyui-site-images.sh generate landing about
./scripts/comfyui-site-images.sh down
```

The `preflight` commands validate target selection, required checkpoint files, and
referenced page/theme context without starting Docker. `generate-staged` also runs
that preflight first now, so commits that do not touch watched files can skip the
ComfyUI/Ollama startup path entirely.

Pre-commit behavior:

- changing `src/pages/index.astro` regenerates the landing-page art
- changing `src/pages/about.astro` regenerates the about-page art
- changing `src/content/blog/welcome.md` regenerates the launch-post art
- changing the ComfyUI manifest or generation scripts regenerates all site art

Prompt generation behavior:

- the hook collects the staged page content plus shared theme files like
  `src/styles/global.css`, `src/components/Header.astro`, and `src/components/Footer.astro`
- Ollama turns that surrounding context into a page-specific prompt
- the generated prompt is blended with the repo’s shared terminal/tmux art direction so the
  imagery stays visually consistent across pages

Running on another machine:

- if this machine is too light for image generation, run the same repo on a stronger Linux box
- the scripts already respect `COMFYUI_API_URL` and `OLLAMA_API_URL`, so you can point the repo
  at remote services instead of local containers if needed
- if you need to commit prompt/config changes from a lightweight machine without generating images
  there, use `COMFYUI_SKIP_GENERATION=1 git commit ...`, then regenerate on the stronger machine
- after generation, commit the refreshed `public/images/generated/` assets back into the repo as
  usual

Generated assets are committed so GitHub Pages serves them as normal static
files.

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
