#!/usr/bin/env python3
"""
Rename work/ and life/ posts to military-date slugs: DDMMMYY-HHMM.md
Also updates pubDate in frontmatter to include time (T09:00:00Z).

Run dry-run first:
  python3 scripts/rename-to-date-slugs.py --dry-run

Apply:
  python3 scripts/rename-to-date-slugs.py
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN',
          'JUL','AUG','SEP','OCT','NOV','DEC']

DRY_RUN = '--dry-run' in sys.argv

COLLECTIONS = [
    Path('src/content/work'),
    Path('src/content/life'),
]

# Regex to match already-converted slugs like 03JAN00-0900
ALREADY = re.compile(r'^\d{2}[A-Z]{3}\d{2}-\d{4}$')

PUBDATE_RE = re.compile(
    r"^pubDate:\s*['\"]?([^'\"\n]+?)['\"]?\s*$",
    re.M
)


def to_mil_slug(dt: datetime) -> str:
    day   = f"{dt.day:02d}"
    mon   = MONTHS[dt.month - 1]
    yr    = f"{dt.year % 100:02d}"
    hhmm  = f"{dt.hour:02d}{dt.minute:02d}"
    return f"{day}{mon}{yr}-{hhmm}"


def parse_date(raw: str) -> datetime | None:
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d',
                '%b %d %Y', '%B %d %Y'):
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


renamed = 0
skipped = 0

for col in COLLECTIONS:
    if not col.exists():
        print(f"  skip {col} (not found)")
        continue

    files = sorted(col.glob('*.md'))
    seen_slugs: set[str] = set()

    # Build a set of already-used date slugs to detect collisions
    for f in files:
        if ALREADY.match(f.stem):
            seen_slugs.add(f.stem)

    for f in files:
        if ALREADY.match(f.stem):
            skipped += 1
            continue

        text = f.read_text(errors='ignore')
        m = PUBDATE_RE.search(text)
        if not m:
            print(f"  WARN  no pubDate: {f.name}")
            skipped += 1
            continue

        raw_date = m.group(1)
        dt = parse_date(raw_date)
        if not dt:
            print(f"  WARN  unparseable date '{raw_date}': {f.name}")
            skipped += 1
            continue

        # Default fabricated time: 09:00 UTC
        if dt.hour == 0 and dt.minute == 0:
            dt = dt.replace(hour=9, minute=0)

        # Resolve collisions by incrementing hour
        slug = to_mil_slug(dt)
        while slug in seen_slugs:
            dt = dt.replace(hour=dt.hour + 1 if dt.minute == 0 else dt.hour,
                            minute=(dt.minute + 30) % 60)
            slug = to_mil_slug(dt)
        seen_slugs.add(slug)

        new_path = f.parent / f"{slug}.md"

        # Update pubDate in frontmatter to include time
        new_pubdate = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        new_text = PUBDATE_RE.sub(f"pubDate: '{new_pubdate}'", text, count=1)

        print(f"  {'DRY ' if DRY_RUN else ''}RENAME  {f.name}  →  {new_path.name}")

        if not DRY_RUN:
            f.write_text(new_text)
            f.rename(new_path)
        renamed += 1

print(f"\n{'DRY-RUN ' if DRY_RUN else ''}done — renamed: {renamed}, skipped: {skipped}")
