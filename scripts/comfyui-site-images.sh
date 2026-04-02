#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/comfyui-site-images.sh <up|down|generate|generate-staged|preflight|preflight-staged|install-hooks|pull-ollama-model> [targets...]

Examples:
  scripts/comfyui-site-images.sh install-hooks
  scripts/comfyui-site-images.sh preflight landing
  scripts/comfyui-site-images.sh preflight-staged
  scripts/comfyui-site-images.sh up
  scripts/comfyui-site-images.sh generate landing about
  scripts/comfyui-site-images.sh generate-staged
  scripts/comfyui-site-images.sh down
EOF
}

[[ $# -ge 1 ]] || { usage >&2; exit 1; }

command="$1"
shift

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
compose_file="$repo_root/comfyui/docker-compose.yml"
manifest_file="$repo_root/comfyui/site-images.json"
python_script="$repo_root/scripts/comfyui-site-images.py"
comfyui_api_url="${COMFYUI_API_URL:-http://127.0.0.1:8188}"
ollama_api_url="${OLLAMA_API_URL:-http://127.0.0.1:11434}"
# Inside the generator container, services are reachable by name
generator_comfyui_url="http://comfyui:8188"
generator_ollama_url="http://ollama:11434"

docker_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
    return
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
    return
  fi

  echo "error: docker compose is required" >&2
  exit 1
}

wait_for_comfyui() {
  local attempts=0

  while (( attempts < 60 )); do
    if curl --silent --fail "$comfyui_api_url/system_stats" >/dev/null; then
      return 0
    fi

    attempts=$((attempts + 1))
    sleep 2
  done

  echo "error: ComfyUI API did not become ready at $comfyui_api_url" >&2
  exit 1
}

wait_for_ollama() {
  local attempts=0

  while (( attempts < 60 )); do
    if curl --silent --fail "$ollama_api_url/api/tags" >/dev/null; then
      return 0
    fi

    attempts=$((attempts + 1))
    sleep 2
  done

  echo "error: Ollama API did not become ready at $ollama_api_url" >&2
  exit 1
}

run_generator() {
  docker_compose_cmd -f "$compose_file" run --rm \
    --no-TTY \
    generator python3 /repo/scripts/comfyui-site-images.py "$@"
}

preflight_generation() {
  run_generator \
    --repo-root /repo \
    --manifest /repo/comfyui/site-images.json \
    --api-url "$generator_comfyui_url" \
    --ollama-url "$generator_ollama_url" \
    --preflight \
    "$@"
}

capture_preflight_status() {
  set +e
  preflight_generation "$@"
  preflight_status=$?
  set -e
}

ensure_stack() {
  local ollama_ready=0
  local comfyui_ready=0

  if curl --silent --fail "$ollama_api_url/api/tags" >/dev/null 2>&1; then
    ollama_ready=1
  fi

  if curl --silent --fail "$comfyui_api_url/system_stats" >/dev/null 2>&1; then
    comfyui_ready=1
  fi

  if (( ollama_ready == 0 && comfyui_ready == 0 )); then
    docker_compose_cmd -f "$compose_file" up -d ollama comfyui
  elif (( ollama_ready == 1 && comfyui_ready == 0 )); then
    docker_compose_cmd -f "$compose_file" up -d comfyui
  elif (( ollama_ready == 0 && comfyui_ready == 1 )); then
    docker_compose_cmd -f "$compose_file" up -d ollama
  fi

  wait_for_ollama
  wait_for_comfyui
}

ollama_model() {
  python3 - "$manifest_file" <<'PY'
from __future__ import annotations
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)

print(data["prompt_generation"]["ollama_model"])
PY
}

case "$command" in
  install-hooks)
    git -C "$repo_root" config core.hooksPath .githooks
    ;;
  up)
    ensure_stack
    ;;
  down)
    docker_compose_cmd -f "$compose_file" down
    ;;
  pull-ollama-model)
    ensure_stack
    docker_compose_cmd -f "$compose_file" exec -T ollama ollama pull "$(ollama_model)"
    ;;
  preflight)
    capture_preflight_status "$@"
    [[ $preflight_status -eq 11 ]] && exit 0
    exit "$preflight_status"
    ;;
  preflight-staged)
    capture_preflight_status --targets-from-staged
    [[ $preflight_status -eq 11 ]] && exit 0
    exit "$preflight_status"
    ;;
  generate)
    capture_preflight_status "$@"
    [[ $preflight_status -eq 11 ]] && exit 0
    [[ $preflight_status -ne 0 ]] && exit "$preflight_status"
    ensure_stack
    run_generator \
      --repo-root /repo \
      --manifest /repo/comfyui/site-images.json \
      --api-url "$generator_comfyui_url" \
      --ollama-url "$generator_ollama_url" \
      "$@"
    ;;
  generate-staged)
    capture_preflight_status --targets-from-staged
    [[ $preflight_status -eq 11 ]] && exit 0
    [[ $preflight_status -ne 0 ]] && exit "$preflight_status"
    ensure_stack
    run_generator \
      --repo-root /repo \
      --manifest /repo/comfyui/site-images.json \
      --api-url "$generator_comfyui_url" \
      --ollama-url "$generator_ollama_url" \
      --targets-from-staged
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "error: unsupported command: $command" >&2
    exit 1
    ;;
esac
