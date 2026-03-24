#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from textwrap import shorten


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and copy ComfyUI-generated site imagery into public assets."
    )
    parser.add_argument("targets", nargs="*", help="Target names from comfyui/site-images.json")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--ollama-url", required=True)
    parser.add_argument(
        "--targets-from-staged",
        action="store_true",
        help="Resolve targets from staged Git paths instead of explicit target names.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def staged_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def staged_file_content(repo_root: Path, relative_path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f":{relative_path}"],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def resolve_targets(manifest: dict, changed_paths: list[str]) -> list[str]:
    changed = set(changed_paths)
    if not changed:
        return []

    if changed.intersection(manifest.get("regenerate_all_on", [])):
        return sorted(manifest["targets"].keys())

    selected: list[str] = []
    for name, config in manifest["targets"].items():
        if changed.intersection(config.get("watch", [])):
            selected.append(name)
    return selected


def ensure_model_exists(repo_root: Path, model_name: str) -> None:
    model_path = repo_root / "comfyui" / "models" / "checkpoints" / model_name
    if not model_path.exists():
        raise FileNotFoundError(
            f"missing checkpoint {model_name!r} at {model_path}. "
            "Place the model in comfyui/models/checkpoints/ before generating imagery."
        )


def request_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.load(response)


def request_ollama_prompt(
    ollama_url: str,
    model_name: str,
    theme_brief: str,
    context_block: str,
    art_direction: str,
    negative_prompt_seed: str,
) -> dict:
    system_prompt = (
        "You create concise, production-ready image prompts for ComfyUI text-to-image generation. "
        "Return strict JSON with exactly two string keys: prompt and negative_prompt. "
        "Keep the visual language cohesive with the provided theme brief. "
        "Do not include markdown, code fences, or commentary."
    )
    user_prompt = (
        f"Theme brief:\n{theme_brief}\n\n"
        f"Target art direction:\n{art_direction}\n\n"
        f"Negative prompt seed:\n{negative_prompt_seed}\n\n"
        f"Relevant page and theme context:\n{context_block}\n"
    )
    payload = {
        "model": model_name,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "format": "json",
    }
    response = request_json(f"{ollama_url.rstrip('/')}/api/generate", payload)
    content = json.loads(response["response"])
    return {
        "prompt": content["prompt"],
        "negative_prompt": content["negative_prompt"],
    }


def read_context_excerpt(
    repo_root: Path, relative_path: str, staged_changed_paths: set[str], limit: int = 5000
) -> str:
    staged_content = None
    if relative_path in staged_changed_paths:
        staged_content = staged_file_content(repo_root, relative_path)

    if staged_content is not None:
        content = staged_content
    else:
        content = (repo_root / relative_path).read_text(encoding="utf-8")
    return shorten(" ".join(content.split()), width=limit, placeholder=" ...")


def build_context_block(
    repo_root: Path,
    manifest: dict,
    target_name: str,
    config: dict,
    staged_changed_paths: set[str],
) -> str:
    prompt_generation = manifest["prompt_generation"]
    paths = list(prompt_generation.get("shared_context", [])) + list(config.get("context", []))
    blocks: list[str] = []
    for relative_path in paths:
        absolute_path = repo_root / relative_path
        if not absolute_path.exists():
            raise FileNotFoundError(f"missing context file for {target_name}: {relative_path}")
        blocks.append(
            f"FILE: {relative_path}\n"
            f"{read_context_excerpt(repo_root, relative_path, staged_changed_paths)}"
        )
    return "\n\n".join(blocks)


def build_prompt_graph(
    config: dict,
    model_name: str,
    prefix: str,
    positive_prompt: str,
    negative_prompt: str,
) -> dict:
    return {
        "1": {"inputs": {"ckpt_name": model_name}, "class_type": "CheckpointLoaderSimple"},
        "2": {
            "inputs": {"text": positive_prompt, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {"text": negative_prompt, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {
                "width": config["width"],
                "height": config["height"],
                "batch_size": 1,
            },
            "class_type": "EmptyLatentImage",
        },
        "5": {
            "inputs": {
                "seed": config["seed"],
                "steps": config["steps"],
                "cfg": config["cfg"],
                "sampler_name": config["sampler_name"],
                "scheduler": config["scheduler"],
                "denoise": 1,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
            "class_type": "KSampler",
        },
        "6": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
        "7": {
            "inputs": {"filename_prefix": prefix, "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }


def wait_for_output(api_url: str, prompt_id: str) -> dict:
    history_url = f"{api_url.rstrip('/')}/history/{prompt_id}"
    for _ in range(180):
        history = fetch_json(history_url)
        prompt_history = history.get(prompt_id)
        if prompt_history and prompt_history.get("outputs"):
            return prompt_history
        time.sleep(2)
    raise TimeoutError(f"timed out waiting for ComfyUI history for prompt {prompt_id}")


def copy_generated_file(repo_root: Path, prompt_history: dict, destination: Path) -> Path:
    for node_output in prompt_history["outputs"].values():
        for image in node_output.get("images", []):
            source = repo_root / "comfyui" / "output"
            if image.get("subfolder"):
                source = source / image["subfolder"]
            source = source / image["filename"]
            if source.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                return source
    raise FileNotFoundError("ComfyUI finished without a readable generated image in comfyui/output/")


def write_metadata(
    repo_root: Path,
    destination: Path,
    target_name: str,
    config: dict,
    prompt_id: str,
    source_path: Path,
) -> None:
    metadata = {
        "target": target_name,
        "prompt_id": prompt_id,
        "source_output": str(source_path.relative_to(repo_root)),
        "prompt": config["prompt"],
        "negative_prompt": config["negative_prompt"],
        "ollama_model": config["ollama_model"],
        "context_files": config["context_files"],
        "width": config["width"],
        "height": config["height"],
        "steps": config["steps"],
        "cfg": config["cfg"],
        "sampler_name": config["sampler_name"],
        "scheduler": config["scheduler"],
        "seed": config["seed"],
    }
    metadata_path = destination.with_suffix(".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def render_target(
    repo_root: Path,
    manifest: dict,
    api_url: str,
    ollama_url: str,
    target_name: str,
    staged_changed_paths: set[str],
) -> None:
    config = manifest["targets"][target_name]
    model_name = config.get("model", manifest["default_model"])
    ensure_model_exists(repo_root, model_name)

    prompt_generation = manifest["prompt_generation"]
    context_files = prompt_generation.get("shared_context", []) + config.get("context", [])
    context_block = build_context_block(
        repo_root, manifest, target_name, config, staged_changed_paths
    )
    prompt_bundle = request_ollama_prompt(
        ollama_url=ollama_url,
        model_name=prompt_generation["ollama_model"],
        theme_brief=prompt_generation["theme_brief"],
        context_block=context_block,
        art_direction=config["art_direction"],
        negative_prompt_seed=config["negative_prompt_seed"],
    )

    positive_prompt = f'{prompt_generation["theme_brief"]} {prompt_bundle["prompt"]}'
    negative_prompt = f'{config["negative_prompt_seed"]}, {prompt_bundle["negative_prompt"]}'
    prompt_graph = build_prompt_graph(
        config,
        model_name,
        f"site/{target_name}",
        positive_prompt,
        negative_prompt,
    )
    response = request_json(f"{api_url.rstrip('/')}/prompt", {"prompt": prompt_graph})
    prompt_id = response["prompt_id"]
    prompt_history = wait_for_output(api_url, prompt_id)

    destination = repo_root / config["output"]
    source_path = copy_generated_file(repo_root, prompt_history, destination)
    write_metadata(
        repo_root,
        destination,
        target_name,
        {
            **config,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "ollama_model": prompt_generation["ollama_model"],
            "context_files": context_files,
        },
        prompt_id,
        source_path,
    )
    print(f"generated {target_name}: {destination.relative_to(repo_root)}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)
    changed_paths = staged_paths(repo_root)

    if args.targets_from_staged:
        targets = resolve_targets(manifest, changed_paths)
    else:
        targets = args.targets or sorted(manifest["targets"].keys())

    unknown = [target for target in targets if target not in manifest["targets"]]
    if unknown:
        raise ValueError(f"unknown targets requested: {', '.join(unknown)}")

    if not targets:
        print("no staged changes require ComfyUI image regeneration", file=sys.stderr)
        return 0

    for target_name in targets:
        render_target(
            repo_root,
            manifest,
            args.api_url,
            args.ollama_url,
            target_name,
            set(changed_paths),
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        FileNotFoundError,
        TimeoutError,
        urllib.error.URLError,
        ValueError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        KeyError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
