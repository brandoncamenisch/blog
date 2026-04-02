#!/usr/bin/env bash
# Generate hero images for work posts (newest → oldest), 100 at a time.
# After each batch, commits and pushes the generated WebP files.
#
# Usage:
#   scripts/generate-images-batch.sh [--batch-size N] [--dry-run] [--no-push]

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
compose_file="$repo_root/comfyui/docker-compose.yml"
batch_size=100
dry_run=0
no_push=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --batch-size) batch_size="$2"; shift 2 ;;
    --dry-run)    dry_run=1; shift ;;
    --no-push)    no_push=1; shift ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

docker_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
    return
  fi
  docker-compose "$@"
}

run_generator() {
  docker_compose_cmd -f "$compose_file" run --rm -T generator python3 "$@"
}

# Get sorted list of targets that still need images (newest pubDate first).
mapfile -t all_targets < <(run_generator \
  /repo/scripts/list-pending-targets.py \
  /repo/comfyui/site-images.json \
  /repo)
total="${#all_targets[@]}"

if [[ $total -eq 0 ]]; then
  echo "✓ All work post images already generated."
  exit 0
fi

echo "→ $total work posts need images (newest first, batch size $batch_size)"

batch_targets=("${all_targets[@]:0:$batch_size}")
batch_count="${#batch_targets[@]}"

echo "→ Generating batch of $batch_count targets..."

if [[ $dry_run -eq 1 ]]; then
  echo "[dry-run] would generate: ${batch_targets[*]}"
  exit 0
fi

# Ensure ComfyUI + Ollama are running (also builds generator image if needed)
"$script_dir/comfyui-site-images.sh" up
docker_compose_cmd -f "$compose_file" build generator

# Generate inside container
run_generator /repo/scripts/comfyui-site-images.py \
  --repo-root /repo \
  --manifest /repo/comfyui/site-images.json \
  --api-url http://comfyui:8188 \
  --ollama-url http://ollama:11434 \
  "${batch_targets[@]}"

# Count images produced
generated=$(find "$repo_root/public/images/generated" -name "*.webp" | wc -l)
echo "→ $generated WebP images present after generation"

# Commit
cd "$repo_root"
git add public/images/generated/ src/content/work/
if ! git diff --cached --quiet; then
  batch_label="${batch_targets[0]}..${batch_targets[-1]}"
  remaining=$(( total - batch_count ))
  git commit -m "feat: generate hero images batch (${batch_count} posts, ${remaining} remaining)

Newest-to-oldest run. WebP at quality 82.
Range: $batch_label

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  echo "✓ Committed $batch_count images"
else
  echo "⚠ Nothing to commit (images may already be staged)"
fi

if [[ $no_push -eq 0 ]]; then
  git push origin main
  echo "✓ Pushed to GitHub"
fi

echo ""
echo "Done. Run again to generate the next batch of up to $batch_size."
echo "Remaining after this batch: $(( total - batch_count ))"
