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
  docker_compose_cmd -f "$compose_file" run --rm --no-TTY generator python3 "$@"
}

# Get sorted list of targets that still need images (newest pubDate first).
# Runs inside generator container so repo is at /repo.
targets_json=$(run_generator - /repo/comfyui/site-images.json /repo <<'PY'
import json, sys, re
from pathlib import Path
from datetime import datetime, timezone

manifest_path, repo_root = sys.argv[1], Path(sys.argv[2])
manifest = json.loads(Path(manifest_path).read_text())
targets = manifest["targets"]

rows = []
for target_name, config in targets.items():
    ctx = config.get("context", [])
    if not ctx:
        continue
    md_rel = ctx[0]
    if not md_rel.startswith("src/content/work/"):
        continue
    md_path = repo_root / md_rel
    if not md_path.exists():
        continue

    output = repo_root / config["output"]
    if output.exists():
        continue

    content = md_path.read_text(encoding="utf-8")
    if "generatedHeroImage" in content:
        continue

    pub_date = datetime.min.replace(tzinfo=timezone.utc)
    m = re.search(r"pubDate:\s*['\"]?([^'\"\n]+)['\"]?", content)
    if m:
        try:
            pub_date = datetime.fromisoformat(m.group(1).strip().replace("Z", "+00:00"))
        except ValueError:
            pass

    rows.append((pub_date, target_name))

rows.sort(key=lambda x: x[0], reverse=True)
print(json.dumps([r[1] for r in rows]))
PY
)

all_targets=($(python3 -c "import json,sys; print(' '.join(json.loads(sys.stdin.read())))" <<< "$targets_json"))
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
