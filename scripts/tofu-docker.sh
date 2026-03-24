#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/tofu-docker.sh <init|plan|apply|destroy|validate|fmt> [tofu args...]

Examples:
  scripts/tofu-docker.sh plan
  scripts/tofu-docker.sh apply -auto-approve

Environment variables are passed through from the current shell, for example:
  CLOUDFLARE_API_TOKEN
  TF_VAR_cloudflare_zone_id
  TF_VAR_blog_subdomain
  TF_VAR_blog_target
  TF_VAR_proxied
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

[[ $# -ge 1 ]] || { usage >&2; exit 1; }

action="$1"
shift

case "$action" in
  init|plan|apply|destroy|validate|fmt)
    ;;
  *)
    echo "error: unsupported tofu action: $action" >&2
    exit 1
    ;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
image_tag="ghcr.io/opentofu/opentofu:1.10.5"
infra_dir="/workspace/infra/cloudflare"

env_args=()
for var_name in \
  CLOUDFLARE_API_TOKEN \
  TF_VAR_cloudflare_zone_id \
  TF_VAR_blog_subdomain \
  TF_VAR_blog_target \
  TF_VAR_proxied
do
  if [[ -v "$var_name" ]]; then
    env_args+=(-e "$var_name")
  fi
done

quoted_args=""
for arg in "$@"; do
  quoted_args+=" $(printf '%q' "$arg")"
done

case "$action" in
  init)
    command_string="tofu -chdir=$infra_dir init$quoted_args"
    ;;
  fmt)
    command_string="tofu -chdir=$infra_dir fmt$quoted_args"
    ;;
  validate)
    command_string="tofu -chdir=$infra_dir init -input=false >/dev/null && tofu -chdir=$infra_dir validate$quoted_args"
    ;;
  *)
    command_string="tofu -chdir=$infra_dir init -input=false >/dev/null && tofu -chdir=$infra_dir $action -input=false$quoted_args"
    ;;
esac

tty_args=()
if [[ -t 0 && -t 1 ]]; then
  tty_args+=(-t)
fi

docker run --rm -i "${tty_args[@]}" \
  --user "$(id -u):$(id -g)" \
  -v "$repo_root:/workspace" \
  "${env_args[@]}" \
  --entrypoint /bin/sh \
  "$image_tag" \
  -lc "$command_string"
