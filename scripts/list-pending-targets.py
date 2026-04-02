#!/usr/bin/env python3
"""List work post targets that still need hero images, sorted newest pubDate first.

Usage: python3 scripts/list-pending-targets.py <manifest> <repo_root>
Prints a newline-separated list of target names.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

manifest_path, repo_root = sys.argv[1], Path(sys.argv[2])
manifest = json.loads(Path(manifest_path).read_text())
targets = manifest["targets"]

rows: list[tuple[datetime, str]] = []
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

    pub_date: datetime = datetime.min.replace(tzinfo=timezone.utc)
    m = re.search(r"pubDate:\s*['\"]?([^'\"\n]+)['\"]?", content)
    if m:
        try:
            pub_date = datetime.fromisoformat(m.group(1).strip().replace("Z", "+00:00"))
        except ValueError:
            pass

    rows.append((pub_date, target_name))

rows.sort(key=lambda x: x[0], reverse=True)
for _, name in rows:
    print(name)
