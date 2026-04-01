#!/usr/bin/env python3
"""
Interactive review workflow for /work posts.

Usage:
  python3 scripts/review-work.py            # review next post
  python3 scripts/review-work.py --auto     # generate all posts automatically
  python3 scripts/review-work.py --auto --limit 20   # generate up to 20
  python3 scripts/review-work.py --auto --delay 2    # 2s pause between posts
  python3 scripts/review-work.py --status   # show queue progress
  python3 scripts/review-work.py --skip     # skip current post
  python3 scripts/review-work.py --back     # go back one post
  python3 scripts/review-work.py --list     # list next 10 in queue

LLM generation uses local Ollama by default (http://localhost:11434).
Override with OLLAMA_HOST and OLLAMA_MODEL env vars.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT  = Path(__file__).parent.parent
WORK_DIR   = REPO_ROOT / "src" / "content" / "work"
STATE_FILE = Path(__file__).parent / ".review-state.json"

# ── Era context: printed alongside each post to seed research ─────────────────
ERA_CONTEXT = [
    (datetime(2000, 1, 1), datetime(2002, 12, 31),
     "Dot-com bust. Linux on the desktop getting serious. Apache, Sendmail, BIND "
     "ruling ops. Y2K aftermath. Early VMware. Napster, early P2P drama. "
     "Sun Microsystems still relevant. IPv6 discussions beginning."),
    (datetime(2003, 1, 1), datetime(2006, 12, 31),
     "Rise of open-source stacks. LAMP everywhere. Xen hypervisor. Google "
     "hiring aggressively. Firefox launch. Web 2.0 coining. Early Digg/Reddit. "
     "Sysadmin role evolving — more scripting, more Python/Perl automation."),
    (datetime(2007, 1, 1), datetime(2009, 12, 31),
     "GitHub launches (2008). AWS EC2/S3 gaining serious traction. iPhone SDK. "
     "Hadoop going mainstream. Git adoption spreading. Cloud vs. colo debates. "
     "Economic crash hitting tech hiring. Agile/Scrum spreading."),
    (datetime(2010, 1, 1), datetime(2012, 12, 31),
     "DevOps term emerging. Chef/Puppet config management wars. Netflix chaos "
     "engineering. OpenStack launch. Heroku selling to Salesforce. "
     "Continuous delivery book published. NoSQL hype peak. AWS re:Invent starts."),
    (datetime(2013, 1, 1), datetime(2015, 12, 31),
     "Docker released (2013) — containers going mainstream. Microservices term "
     "coined. CoreOS, etcd, fleet. Kubernetes announced by Google (2014). "
     "Mesos/Marathon. SRE book writing begins at Google. 12-factor app."),
    (datetime(2016, 1, 1), datetime(2018, 12, 31),
     "Kubernetes winning container wars. Helm, Istio, Envoy emerging. "
     "Serverless/Lambda hype. Terraform 0.x. GitOps term coined. "
     "Prometheus + Grafana replacing Nagios. Platform engineering conversations start."),
    (datetime(2019, 1, 1), datetime(2021, 12, 31),
     "Platform engineering formalizing. Internal developer portals (Backstage). "
     "SRE roles proliferating. COVID driving remote-first infra scaling. "
     "eBPF gaining attention. ArgoCD, Flux GitOps maturing. "
     "Kubernetes complexity fatigue beginning."),
    (datetime(2022, 1, 1), datetime(2024, 12, 31),
     "AI/LLM infrastructure explosion post-ChatGPT. Platform engineering "
     "mainstream. CNCF landscape overwhelming. WebAssembly on server side. "
     "Developer experience as discipline. FinOps, cloud cost pressure. "
     "DORA metrics widely adopted. Staff+ engineering tracks normalized."),
    (datetime(2025, 1, 1), datetime(2026, 12, 31),
     "AI-native tooling everywhere — copilots, agents, LLM-assisted ops. "
     "Platform teams owning AI infra pipelines. eBPF production-proven. "
     "Wasm + containers converging. Multi-cloud as default. "
     "Post-hype Kubernetes: boring and essential. Engineers managing AI context."),
]

def get_era_context(date: datetime) -> str:
    for start, end, text in ERA_CONTEXT:
        if start <= date <= end:
            return text
    return "No era context available."

# ── ANSI helpers ───────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BLUE   = "\033[34m"

def c(text, *codes): return "".join(codes) + str(text) + RESET
def hr(ch="─", width=72): return c(ch * width, DIM)

# ── State persistence ──────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"completed": [], "skipped": []}

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ── Post loading ───────────────────────────────────────────────────────────────
def parse_frontmatter(text: str):
    parts = re.split(r'\n---\n', '\n' + text, 2)
    if len(parts) < 3:
        return {}, text
    fm_raw = parts[1]
    body   = parts[2]
    fm = {}
    for line in fm_raw.splitlines():
        m = re.match(r'^(\w+):\s*(.+)$', line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip("'\"")
    fm["_raw"] = fm_raw
    return fm, body

def load_queue() -> list[dict]:
    posts = []
    for path in WORK_DIR.glob("*.md"):
        text = path.read_text()
        fm, body = parse_frontmatter(text)
        if fm.get("reviewed") == "true":
            continue
        date_str = fm.get("pubDate", "0000-00-00")
        try:
            date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            date = datetime.min
        posts.append({
            "path":     path,
            "slug":     path.stem,
            "date":     date,
            "date_str": date_str[:10],
            "title":    fm.get("title", ""),
            "tags":     fm.get("tags", ""),
            "fm":       fm,
            "body":     body,
            "text":     text,
        })
    posts.sort(key=lambda p: p["date"])
    return posts

# ── Web context fetch ──────────────────────────────────────────────────────────
def fetch_hn_stories(date: datetime) -> list[dict]:
    """Pull top HN stories from that calendar month via Algolia (no auth)."""
    month_start = date.replace(day=1, hour=0, minute=0, second=0)
    if date.month == 12:
        month_end = date.replace(year=date.year+1, month=1, day=1)
    else:
        month_end = date.replace(month=date.month+1, day=1)
    ts_start = int(month_start.timestamp())
    ts_end   = int(month_end.timestamp())
    url = (
        "https://hn.algolia.com/api/v1/search"
        f"?tags=story&numericFilters=created_at_i>{ts_start},created_at_i<{ts_end}"
        "&hitsPerPage=12&attributesToRetrieve=title,url,points,num_comments"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "review-work/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        return data.get("hits", [])
    except Exception as e:
        return []

def format_hn_context(stories: list[dict]) -> str:
    if not stories:
        return "(no HN stories found for this period)"
    lines = []
    for s in stories[:10]:
        title = s.get("title", "")
        pts   = s.get("points", 0)
        cmts  = s.get("num_comments", 0)
        lines.append(f"- {title} ({pts}pts, {cmts} comments)")
    return "\n".join(lines)

# ── Ollama bootstrap ───────────────────────────────────────────────────────────
def ensure_ollama():
    """Make sure ollama is running and the model is pulled."""
    host  = os.environ.get("OLLAMA_HOST",  "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")

    def ping():
        try:
            with urllib.request.urlopen(f"{host}/api/tags", timeout=4) as r:
                return r.status == 200
        except Exception:
            return False

    # 1. Start if not running
    if not ping():
        print(f"  {c('ollama not running — starting...', YELLOW)}")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            print(f"  {c('ERROR: `ollama` binary not found. Install from https://ollama.com', RED)}")
            sys.exit(1)
        for i in range(30):
            time.sleep(0.5)
            if ping():
                print(f"  {c('ollama ready', GREEN)}")
                break
        else:
            print(f"  {c('ERROR: ollama did not respond after 15s', RED)}")
            sys.exit(1)
    else:
        print(f"  {c('ollama running', GREEN)}")

    # 2. Ensure model is present
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=8) as r:
            tags = json.loads(r.read())
        present = [m["name"] for m in tags.get("models", [])]
        model_ok = any(
            p == model or p.split(":")[0] == model.split(":")[0]
            for p in present
        )
    except Exception:
        model_ok = False

    if not model_ok:
        print(f"  {c(f'pulling {model} ...', YELLOW)}")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
        except subprocess.CalledProcessError as e:
            print(f"  {c(f'ERROR: pull failed: {e}', RED)}")
            sys.exit(1)
        print(f"  {c(f'{model} ready', GREEN)}")
    else:
        print(f"  {c(f'model {model} present', GREEN)}")

    return host, model


# ── LLM generation ─────────────────────────────────────────────────────────────
def llm_chat(messages: list[dict]) -> str:
    """Call local Ollama with streaming output, fall back to cloud if unavailable."""

    # ── Ollama (local, streaming) ────────────────────────────────────────────
    ollama_host  = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    try:
        payload = json.dumps({
            "model":    ollama_model,
            "messages": messages,
            "stream":   True,
            "options":  {"temperature": 0.85, "num_predict": 1400},
        }).encode()
        req = urllib.request.Request(
            f"{ollama_host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        chunks = []
        print(f"\n  {c('generating', DIM)} ", end="", flush=True)
        with urllib.request.urlopen(req, timeout=300) as r:
            for raw_line in r:
                line = raw_line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                token = obj.get("message", {}).get("content", "")
                if token:
                    chunks.append(token)
                    print(c("·", DIM), end="", flush=True)
                if obj.get("done"):
                    break
        print()
        return "".join(chunks)
    except Exception as e:
        print(f"\n  {c(f'Ollama error: {e}', YELLOW)}")

    # ── OpenAI ───────────────────────────────────────────────────────────────
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        payload = json.dumps({
            "model": "gpt-4o", "messages": messages,
            "max_tokens": 1200, "temperature": 0.85,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    # ── Anthropic ────────────────────────────────────────────────────────────
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        system    = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]
        payload   = json.dumps({
            "model": "claude-opus-4-5", "max_tokens": 1200,
            "system": system, "messages": user_msgs,
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["content"][0]["text"]

    # ── GitHub Models ────────────────────────────────────────────────────────
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if not gh_token:
        try:
            gh_token = subprocess.check_output(
                ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            pass
    if gh_token:
        payload = json.dumps({
            "model": "gpt-4o", "messages": messages,
            "max_tokens": 1200, "temperature": 0.85,
        }).encode()
        req = urllib.request.Request(
            "https://models.inference.ai.azure.com/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {gh_token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    raise RuntimeError(
        "No LLM available.\n"
        "  Ollama:    ensure `ollama serve` is running (default: http://localhost:11434)\n"
        "  Override:  OLLAMA_HOST=http://... OLLAMA_MODEL=llama3\n"
        "  Cloud:     set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GITHUB_TOKEN"
    )

def build_prompt(post: dict, hn_context: str, era: str) -> list[dict]:
    date_fmt = post["date"].strftime("%B %-d, %Y")
    week_fmt = post["date"].strftime("the week of %B %-d, %Y")
    return [
        {
            "role": "system",
            "content": (
                "You are Brandon Camenisch — an engineering manager and platform engineer "
                "with 20+ years of experience. You write a personal technical blog. "
                "Your voice is direct, experienced, occasionally self-deprecating, and "
                "grounded in real ops and infrastructure work. You don't hype things. "
                "You write about what you actually did, thought, or wrestled with."
            ),
        },
        {
            "role": "user",
            "content": f"""Write a personal blog post for {date_fmt}.

ERA CONTEXT (what was happening in tech at this time):
{era}

TOP HACKER NEWS STORIES FROM THIS MONTH (use as inspiration for the zeitgeist):
{hn_context}

INSTRUCTIONS:
- Write 450–650 words of real blog post content
- Write in first person — this is your journal, your thinking
- Reference specific technologies, tools, or industry events from this era
- Ground it in real work: something you debugged, shipped, argued about, or learned
- Do NOT write a summary of the news — use it only to colour the era
- The tone is personal and honest, not polished
- Output format (exactly):

TITLE: [a specific, honest title — not generic]
---
[post body here, markdown ok, no front matter]
""",
        },
    ]

def generate_post(post: dict) -> bool:
    """Fetch context, call LLM, write generated content. Keep hallucination: true."""
    print(f"\n  {c('Fetching HN stories for', DIM)} {post['date_str'][:7]}...", end="", flush=True)
    stories = fetch_hn_stories(post["date"])
    hn_ctx  = format_hn_context(stories)
    era     = get_era_context(post["date"])
    print(f" {c(f'{len(stories)} found', DIM)}")

    if stories:
        print(f"\n  {c('Top stories:', DIM)}")
        for s in stories[:5]:
            print(f"  {c('·', DIM)} {s.get('title','')[:70]}")

    print(f"\n  {c('Generating post...', CYAN)}", end="", flush=True)
    try:
        messages = build_prompt(post, hn_ctx, era)
        result   = llm_chat(messages)
    except RuntimeError as e:
        print(f"\n\n  {c('ERROR:', RED)} {e}\n")
        return False
    except Exception as e:
        print(f"\n\n  {c('ERROR:', RED)} {e}\n")
        return False
    print(f" {c('done', GREEN)}")

    # Parse TITLE: / --- / body
    title, body = None, None
    if "TITLE:" in result and "---" in result:
        parts = result.split("---", 1)
        title_line = parts[0].strip()
        title = re.sub(r"^TITLE:\s*", "", title_line).strip().strip('"')
        body  = parts[1].strip()
    else:
        title = post["fm"].get("title", post["slug"])
        body  = result.strip()

    # Show preview
    print()
    print(hr())
    print(c(f"  {title}", BOLD))
    print(hr())
    for line in body.splitlines()[:8]:
        print(f"  {line}")
    if body.count('\n') > 8:
        print(f"  {c('...', DIM)}")
    print()

    # Write back — keep hallucination: true, update title/description, replace body
    text = post["path"].read_text()
    # Safe frontmatter split — find closing \n---\n boundary
    fm_match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_match:
        print(f"  {c('ERROR: could not parse frontmatter', RED)}")
        return False
    fm   = fm_match.group(1)
    desc = " ".join(body.split()[:20]).rstrip(".,;") + "..."

    def yaml_dquote(s):
        return s.replace('\\', '\\\\').replace('"', '\\"')

    # Anchor replacements to line start
    fm = re.sub(r'(?m)^title:.*$',       f'title: "{yaml_dquote(title)}"',       fm)
    fm = re.sub(r'(?m)^description:.*$', f'description: "{yaml_dquote(desc)}"',  fm)

    post["path"].write_text(f"---\n{fm}\n---\n\n{body}\n")

    # Rename to date-based slug if not already in that format
    _MIL_SLUG = re.compile(r'^\d{2}[A-Z]{3}\d{2}-\d{4}$')
    if not _MIL_SLUG.match(post["path"].stem):
        _MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN',
                   'JUL','AUG','SEP','OCT','NOV','DEC']
        pd_m = re.search(r"^pubDate:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.M)
        if pd_m:
            raw = pd_m.group(1).strip()
            dt  = None
            for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%d', '%b %d %Y', '%B %d %Y'):
                try:
                    dt = datetime.strptime(raw, fmt)
                    break
                except ValueError:
                    pass
            if dt:
                if dt.hour == 0 and dt.minute == 0:
                    dt = dt.replace(hour=9)
                mil = (f"{dt.day:02d}{_MONTHS[dt.month-1]}"
                       f"{dt.year%100:02d}-{dt.hour:02d}{dt.minute:02d}")
                new_path = post["path"].parent / f"{mil}.md"
                if not new_path.exists():
                    post["path"].rename(new_path)
                    post["path"] = new_path
                    post["slug"] = mil

    print(f"\n  {c('✓ Written (still hallucination):', GREEN)} {post['slug']}\n")
    return True

# ── Review action ──────────────────────────────────────────────────────────────
def mark_reviewed(post: dict):
    text = post["path"].read_text()
    fm_match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_match:
        return
    fm   = fm_match.group(1)
    rest = text[fm_match.end():]
    fm = re.sub(r'(?m)^\nhallucination:.*$', '', fm)
    fm = re.sub(r'(?m)^hallucination:.*$', '', fm)
    if re.search(r'(?m)^reviewed:', fm):
        fm = re.sub(r'(?m)^reviewed:.*$', 'reviewed: true', fm)
    else:
        fm = fm.rstrip("\n") + "\nreviewed: true"
    post["path"].write_text(f"---\n{fm}\n---\n{rest}")

def open_in_editor(post: dict):
    editor = os.environ.get("EDITOR", "vim")
    subprocess.call([editor, str(post["path"])])

# ── Search URL ─────────────────────────────────────────────────────────────────
def search_url(date: datetime) -> str:
    week_start = (date - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
    week_end   = (date - timedelta(days=date.weekday()) + timedelta(days=6)).strftime("%Y-%m-%d")
    q = f"tech news week of {week_start}"
    return f"https://duckduckgo.com/?q={urllib.parse.quote(q)}"

def hn_url(date: datetime) -> str:
    # HN Algolia search scoped to that month
    after  = date.strftime("%Y-%m-01")
    before = (date.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m-%d")
    return f"https://hn.algolia.com/?dateRange=custom&dateStart={after}&dateEnd={before}&sort=byPopularity&type=story"

# ── Display ────────────────────────────────────────────────────────────────────
def print_post(post: dict, index: int, total: int):
    print()
    print(hr("═"))
    print(c(f"  WORK REVIEW  [{index + 1} / {total}]", BOLD, CYAN))
    print(hr("═"))
    print(f"  {c('date  ', DIM)} {c(post['date_str'], YELLOW, BOLD)}"
          f"  {c(post['date'].strftime('%A, %B %-d %Y'), DIM)}")
    print(f"  {c('slug  ', DIM)} {post['slug']}")
    print(f"  {c('tags  ', DIM)} {post['tags']}")
    print(f"  {c('file  ', DIM)} {post['path'].relative_to(REPO_ROOT)}")
    print()
    print(hr())
    print(c("  ERA CONTEXT", BOLD))
    print()
    for line in textwrap.wrap(get_era_context(post["date"]), 68):
        print(f"  {line}")
    print()
    print(hr())
    print(c("  RESEARCH LINKS", BOLD))
    print(f"  {c('web  ', DIM)} {search_url(post['date'])}")
    print(f"  {c(' hn  ', DIM)} {hn_url(post['date'])}")
    print()
    print(hr())
    print(c("  CURRENT CONTENT", BOLD))
    print()
    for line in post["body"].strip().splitlines():
        print(f"  {c(line, DIM)}")
    print()
    print(hr("─"))

def print_status(queue: list, state: dict):
    total_orig = len(queue) + len(state["completed"])
    done  = len(state["completed"])
    skip  = len(state["skipped"])
    remain = len(queue)
    pct   = int(done / total_orig * 100) if total_orig else 0
    bar_w = 40
    filled = int(bar_w * done / total_orig) if total_orig else 0
    bar = c("█" * filled, GREEN) + c("░" * (bar_w - filled), DIM)
    print()
    print(hr("═"))
    print(c("  REVIEW PROGRESS — /work", BOLD, CYAN))
    print(hr("═"))
    print(f"  [{bar}] {c(f'{pct}%', BOLD)}")
    print(f"  {c('reviewed', GREEN)}  {done:>6}")
    print(f"  {c('skipped ', YELLOW)}  {skip:>6}")
    print(f"  {c('remaining', DIM)} {remain:>6}")
    print()
    if queue:
        print(c("  Next up:", DIM))
        for p in queue[:5]:
            print(f"  {c(p['date_str'], YELLOW)}  {p['slug'][:55]}")
    print(hr("═"))
    print()

def prompt_action() -> str:
    print(f"  {c('[e]', BOLD)}dit   {c('[g]', BOLD)}enerate   {c('[s]', BOLD)}kip   "
          f"{c('[b]', BOLD)}ack   {c('[m]', BOLD)}ark done   {c('[q]', BOLD)}uit")
    print()
    try:
        return input("  > ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return "q"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Interactive /work post review")
    parser.add_argument("--status", action="store_true", help="Show queue progress")
    parser.add_argument("--skip",   action="store_true", help="Skip current post")
    parser.add_argument("--back",   action="store_true", help="Un-skip last skipped post")
    parser.add_argument("--list",   action="store_true", help="List next posts in queue")
    parser.add_argument("--auto",   action="store_true", help="Auto-generate all posts without input")
    parser.add_argument("--limit",  type=int, default=0,   metavar="N", help="Max posts to process in --auto mode")
    parser.add_argument("--delay",  type=float, default=0, metavar="S", help="Seconds to pause between posts in --auto mode")
    args = parser.parse_args()

    state = load_state()
    queue = [p for p in load_queue()
             if p["slug"] not in state["completed"]
             and p["slug"] not in state["skipped"]]

    if args.status:
        print_status(queue, state)
        return

    if args.list:
        print()
        for i, p in enumerate(queue[:20]):
            print(f"  {c(p['date_str'], YELLOW)}  {p['slug'][:60]}")
        print()
        return

    if args.back:
        if state["skipped"]:
            restored = state["skipped"].pop()
            save_state(state)
            print(f"\n  {c('Restored:', GREEN)} {restored}\n")
        else:
            print("\n  Nothing to restore.\n")
        return

    if args.skip:
        if not queue:
            print("\n  Queue is empty — all posts reviewed!\n")
            return
        post = queue[0]
        state["skipped"].append(post["slug"])
        save_state(state)
        print(f"\n  {c('Skipped:', YELLOW)} {post['slug']}\n")
        return

    # ── Auto mode ─────────────────────────────────────────────────────────────
    if args.auto:
        target = args.limit if args.limit > 0 else len(queue)
        batch  = queue[:target]
        total  = len(batch)

        if not batch:
            print(f"\n  {c('Queue is empty — nothing to generate.', GREEN, BOLD)}\n")
            return

        print()
        print(hr("═"))
        print(c(f"  AUTO MODE  —  {total} post{'s' if total != 1 else ''} to generate", BOLD, CYAN))
        if args.delay:
            print(c(f"  delay {args.delay}s between posts", DIM))
        print(hr("═"))
        print()
        ensure_ollama()

        generated = 0
        try:
            for idx, post in enumerate(batch):
                bar_w   = 36
                filled  = int(bar_w * idx / total)
                bar     = c("█" * filled, GREEN) + c("░" * (bar_w - filled), DIM)
                print(f"  [{bar}] {c(f'{idx+1}/{total}', BOLD)}  {c(post['date_str'], YELLOW)}  {post['slug'][:45]}")

                ok = generate_post(post)
                if ok:
                    state["completed"].append(post["slug"])
                    if post["slug"] in state["skipped"]:
                        state["skipped"].remove(post["slug"])
                    save_state(state)
                    generated += 1
                else:
                    print(f"  {c('⚠ generation failed, skipping', YELLOW)}  {post['slug']}")

                if args.delay and idx < total - 1:
                    time.sleep(args.delay)

        except KeyboardInterrupt:
            print(f"\n\n  {c('Interrupted — progress saved.', YELLOW)}\n")

        print()
        print(hr("═"))
        print(c(f"  AUTO COMPLETE  —  {generated} generated", BOLD, GREEN))
        print(hr("═"))
        print()
        remaining = [p for p in load_queue()
                     if p["slug"] not in state["completed"]
                     and p["slug"] not in state["skipped"]]
        print_status(remaining, state)
        return

    # Interactive review loop
    if not queue:
        print(f"\n  {c('✓ All posts reviewed!', GREEN, BOLD)}\n")
        print_status(queue, state)
        return

    i = 0
    while i < len(queue):
        post = queue[i]
        print_post(post, i, len(queue))
        action = prompt_action()

        if action in ("e", "edit", ""):
            open_in_editor(post)
            print()
            print(f"  {c('[m]', BOLD)}ark reviewed   {c('[s]', BOLD)}kip   {c('[q]', BOLD)}uit")
            try:
                action = input("  > ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                action = "q"

        elif action in ("g", "generate", "gen"):
            ensure_ollama()
            generate_post(post)
            # Stay on this post so user can review/edit what was generated
            continue

        if action in ("m", "mark", "done"):
            mark_reviewed(post)
            state["completed"].append(post["slug"])
            if post["slug"] in state["skipped"]:
                state["skipped"].remove(post["slug"])
            save_state(state)
            print(f"\n  {c('✓ Marked reviewed:', GREEN)} {post['slug']}\n")
            i += 1

        elif action in ("s", "skip"):
            state["skipped"].append(post["slug"])
            save_state(state)
            print(f"\n  {c('→ Skipped:', YELLOW)} {post['slug']}\n")
            i += 1

        elif action in ("b", "back"):
            i = max(0, i - 1)

        elif action in ("q", "quit", "exit"):
            print(f"\n  {c('Session saved. Resume anytime.', DIM)}\n")
            print_status([p for p in queue[i:]], state)
            sys.exit(0)

    print(f"\n  {c('✓ Session complete!', GREEN, BOLD)}\n")
    print_status([], state)

if __name__ == "__main__":
    main()
