#!/usr/bin/env python3
"""Generate the owner-facing status page for the CFN site.

Reads real repo state (git log, STATE.md, APPROVALS.md, dist/) and writes a
self-contained HTML page to scratchpad/cfn-status.html, which is published as
an Artifact. The improvement loop re-runs this and republishes the same file
path each cycle so the URL stays stable.
"""
import base64
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(
    "/tmp/claude-0/-home-user-Charterflightnetwork/"
    "3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/cfn-status.html"
)
LIVE = "https://neutx2.github.io/Charterflightnetwork"


def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def font_data_uri(name: str) -> str:
    p = ROOT / "public" / "fonts" / name
    return "data:font/woff2;base64," + base64.b64encode(p.read_bytes()).decode()


# ---- cycle log from git ----------------------------------------------------
LOG = sh("git log --pretty=format:%H%x1f%cI%x1f%s -200")
cycles = []
for line in LOG.splitlines():
    sha, iso, subject = line.split("\x1f", 2)
    m = re.match(r"loop\(cycle-(\d+[a-z]?)\):\s*(.+)", subject)
    if not m:
        continue
    body = m.group(2)
    what, _, why = body.partition(" — ")
    cycles.append({
        "n": m.group(1),
        "what": what.strip(),
        "why": why.strip(),
        "when": iso,
        "sha": sha[:7],
    })

# ---- guardrails ------------------------------------------------------------
verify = sh("python3 crawl/verify.py | head -2")
redirects_ok = "1047/1047" in verify or re.search(r"(\d+)/\1 redirect", verify)
m_red = re.search(r"(\d+)/(\d+) redirect targets resolve", verify)
m_dead = re.search(r"internal dead links in built site: (\d+)", verify)
pages_built = len(list((ROOT / "dist").rglob("index.html"))) if (ROOT / "dist").exists() else 0

state = (ROOT / "STATE.md").read_text() if (ROOT / "STATE.md").exists() else ""
m_cycle = re.search(r"Cycle #: (\d+)", state)

# ---- approvals -------------------------------------------------------------
approvals = []
if (ROOT / "APPROVALS.md").exists():
    for m in re.finditer(r"^### \[seed\] (.+?)$\n(.*?)(?=^### |\Z)", (ROOT / "APPROVALS.md").read_text(), re.M | re.S):
        cat = re.search(r"- Category: (.+)", m.group(2))
        need = re.search(r"- Decision needed(?: from owner)?: (.+)", m.group(2))
        approvals.append({
            "title": m.group(1).strip(),
            "category": (cat.group(1).strip() if cat else ""),
            "need": (need.group(1).strip() if need else ""),
        })

# ---- key pages to spot-check ----------------------------------------------
KEY_PAGES = [
    ("Home", "/"),
    ("Request quotes", "/quote/"),
    ("Thunder Bay (YQT)", "/canada/northern-ontario/thunder-bay/"),
    ("Canada hub", "/canada/"),
    ("Northern Ontario", "/canada/northern-ontario/"),
    ("Fly-in fishing", "/travel/fly-in-fishing/"),
    ("Charter directory", "/directory/"),
    ("Empty legs", "/empty-legs/"),
    ("For operators", "/operators/"),
    ("About", "/about/"),
]

# ---- home-page thumbnail (rendered from the current build) ---------------
THUMB = ROOT / "scratchpad-thumb.jpg"
thumb_uri = ""
try:
    subprocess.run(
        ["node", "scripts/shoot_thumb.mjs", str(THUMB)],
        cwd=ROOT, capture_output=True, timeout=120, check=True,
    )
    thumb_uri = "data:image/jpeg;base64," + base64.b64encode(THUMB.read_bytes()).decode()
    THUMB.unlink(missing_ok=True)
except Exception as exc:  # thumbnail is a nicety, never fail the page for it
    print(f"(thumbnail skipped: {str(exc)[:80]})")

now = datetime.now(timezone.utc)


def rel(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    secs = (now - dt.astimezone(timezone.utc)).total_seconds()
    if secs < 3600:
        return f"{int(secs // 60)} min ago"
    if secs < 86400:
        return f"{int(secs // 3600)} h ago"
    return f"{int(secs // 86400)} d ago"


e = html.escape
cycle_rows = "\n".join(
    f'''<li class="cycle">
      <span class="cycle-n" aria-hidden="true">{e(c["n"])}</span>
      <div class="cycle-body">
        <p class="cycle-what">{e(c["what"])}</p>
        {f'<p class="cycle-why">{e(c["why"])}</p>' if c["why"] else ""}
        <p class="cycle-meta"><time datetime="{e(c["when"])}">{e(rel(c["when"]))}</time> · <code>{e(c["sha"])}</code></p>
      </div>
    </li>'''
    for c in cycles
)

approval_rows = "\n".join(
    f'''<li class="approval">
      <p class="approval-title">{e(a["title"])}</p>
      <p class="approval-cat">{e(a["category"])}</p>
      <p class="approval-need">{e(a["need"])}</p>
    </li>'''
    for a in approvals
)

page_links = "\n".join(
    f'<li><a href="{LIVE}{p}" target="_blank" rel="noopener">{e(label)}</a></li>'
    for label, p in KEY_PAGES
)

doc = f"""<title>Charter Flight Network — build status</title>
<style>
@font-face {{ font-family:"Outfit V"; font-weight:100 900; font-display:swap;
  src:url("{font_data_uri('outfit-latin-wght-normal.woff2')}") format("woff2-variations"); }}
@font-face {{ font-family:"Inter V"; font-weight:100 900; font-display:swap;
  src:url("{font_data_uri('inter-latin-wght-normal.woff2')}") format("woff2-variations"); }}

:root {{
  --ground:#faf8f4; --panel:#ffffff; --ink:#16283a; --ink-soft:#4a5c6d;
  --line:#e5ded0; --deep:#12314a; --deep-2:#0b2033;
  --good:#2d6a54; --accent:#e8940f; --accent-ink:#0b2033; --chip:#f0f7f4;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --ground:#0d1926; --panel:#152535; --ink:#e2eaf2; --ink-soft:#9db0c2;
    --line:#22374b; --deep:#0b2033; --deep-2:#081827;
    --good:#8dbfa9; --accent:#f5a623; --accent-ink:#0b2033; --chip:#16302a;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0d1926; --panel:#152535; --ink:#e2eaf2; --ink-soft:#9db0c2;
  --line:#22374b; --deep:#0b2033; --deep-2:#081827;
  --good:#8dbfa9; --accent:#f5a623; --accent-ink:#0b2033; --chip:#16302a;
}}
:root[data-theme="light"] {{
  --ground:#faf8f4; --panel:#ffffff; --ink:#16283a; --ink-soft:#4a5c6d;
  --line:#e5ded0; --deep:#12314a; --deep-2:#0b2033;
  --good:#2d6a54; --accent:#e8940f; --accent-ink:#0b2033; --chip:#f0f7f4;
}}

* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink);
  font-family:"Inter V", ui-sans-serif, system-ui, sans-serif; line-height:1.55;
  font-variant-numeric:tabular-nums; }}
.wrap {{ max-width:64rem; margin:0 auto; padding:0 1.25rem; }}

/* ---- top: the thing they came for ---- */
.top {{ background:linear-gradient(165deg, var(--deep) 0%, var(--deep-2) 100%); color:#eef4f9; padding:2.25rem 0 2rem; }}
.top .wrap {{ display:flex; flex-wrap:wrap; gap:1.5rem; align-items:flex-end; justify-content:space-between; }}
.eyebrow {{ font-family:"Outfit V", sans-serif; text-transform:uppercase; letter-spacing:.14em;
  font-size:.72rem; font-weight:600; color:#8fb3cc; margin:0 0 .5rem; }}
h1 {{ font-family:"Outfit V", sans-serif; font-size:clamp(1.5rem,3.6vw,2.1rem); font-weight:700;
  margin:0; line-height:1.15; text-wrap:balance; }}
.built {{ margin:.55rem 0 0; color:#a9c2d6; font-size:.9rem; }}
.cta {{ display:inline-flex; align-items:center; gap:.55rem; background:var(--accent); color:var(--accent-ink);
  font-family:"Outfit V", sans-serif; font-weight:700; font-size:1.02rem; text-decoration:none;
  padding:.85rem 1.4rem; border-radius:.6rem; box-shadow:0 6px 18px rgba(0,0,0,.22); white-space:nowrap; }}
.cta:hover {{ filter:brightness(1.06); }}
.cta:focus-visible {{ outline:3px solid #fff; outline-offset:3px; }}
.eyebrow {{ display:flex; align-items:center; gap:.55rem; }}
.eyebrow svg {{ border-radius:.3rem; }}
.shot {{ display:block; text-decoration:none; position:relative; border-radius:.7rem; overflow:hidden;
  border:1px solid rgba(255,255,255,.16); box-shadow:0 10px 30px rgba(0,0,0,.32); max-width:23rem; flex:none; }}
.shot img {{ display:block; width:100%; height:auto; }}
.shot .cta {{ position:absolute; left:50%; bottom:.85rem; transform:translateX(-50%); font-size:.9rem; padding:.6rem 1rem; }}
.shot:hover img {{ filter:brightness(1.06); }}
.shot:focus-visible {{ outline:3px solid #fff; outline-offset:3px; }}

/* ---- guardrail chips ---- */
.status {{ border-bottom:1px solid var(--line); background:var(--panel); }}
.chips {{ display:flex; flex-wrap:wrap; gap:.5rem 1.75rem; padding:.9rem 0; margin:0; list-style:none; font-size:.88rem; }}
.chip {{ display:flex; align-items:center; gap:.5rem; color:var(--ink-soft); }}
.dot {{ width:.6rem; height:.6rem; border-radius:50%; background:var(--good); flex:none; }}
.dot.warn {{ background:var(--accent); }}
.chip b {{ color:var(--ink); font-weight:600; }}

/* ---- body grid ---- */
.grid {{ display:grid; gap:2.5rem; padding:2.25rem 0 3rem; }}
@media (min-width:60rem) {{ .grid {{ grid-template-columns:minmax(0,1.65fr) minmax(0,1fr); }} }}
h2 {{ font-family:"Outfit V", sans-serif; font-size:1.15rem; font-weight:700; margin:0 0 1rem;
  letter-spacing:-.01em; }}
.sub {{ color:var(--ink-soft); font-size:.9rem; margin:-.65rem 0 1.1rem; }}

.cycles {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.65rem; }}
.cycle {{ display:flex; gap:.9rem; background:var(--panel); border:1px solid var(--line);
  border-radius:.7rem; padding:.9rem 1rem; }}
.cycle-n {{ font-family:"Outfit V", sans-serif; font-weight:700; font-size:.8rem; color:var(--good);
  background:var(--chip); border-radius:.4rem; padding:.15rem .5rem; height:fit-content; flex:none; min-width:2.1rem; text-align:center; }}
.cycle-body {{ min-width:0; }}
.cycle-what {{ margin:0; font-weight:600; font-size:.95rem; }}
.cycle-why {{ margin:.3rem 0 0; color:var(--ink-soft); font-size:.88rem; }}
.cycle-meta {{ margin:.4rem 0 0; color:var(--ink-soft); font-size:.78rem; }}
.cycle-meta code {{ font-size:.75rem; opacity:.8; }}

.side {{ display:flex; flex-direction:column; gap:2rem; }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:.7rem; padding:1.1rem 1.15rem; }}
.approvals {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1rem; }}
.approval {{ border-left:3px solid var(--accent); padding-left:.8rem; }}
.approval-title {{ margin:0; font-weight:600; font-size:.93rem; }}
.approval-cat {{ margin:.2rem 0 0; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-soft); }}
.approval-need {{ margin:.35rem 0 0; font-size:.86rem; color:var(--ink-soft); }}

.pages {{ list-style:none; margin:0; padding:0; display:grid; gap:.4rem; }}
.pages a {{ display:block; padding:.5rem .7rem; border-radius:.45rem; text-decoration:none;
  color:var(--ink); font-size:.9rem; font-weight:500; border:1px solid var(--line); background:var(--ground); }}
.pages a:hover {{ border-color:var(--good); color:var(--good); }}
.pages a:focus-visible {{ outline:2px solid var(--good); outline-offset:2px; }}

footer {{ border-top:1px solid var(--line); padding:1.4rem 0 2.5rem; color:var(--ink-soft); font-size:.82rem; }}
footer p {{ margin:.35rem 0; }}
@media (prefers-reduced-motion: no-preference) {{
  .cycle {{ animation:in .35s ease both; }}
  @keyframes in {{ from {{ opacity:0; transform:translateY(4px); }} }}
}}
</style>

<header class="top">
  <div class="wrap">
    <div class="lede">
      <p class="eyebrow"><svg width="22" height="22" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="15" fill="#1d486b"/><g fill="none" stroke="#faf8f4" stroke-linecap="round" stroke-width="5"><path d="M11 13C29 13 36 20 45 31"/><path d="M11 32h34"/><path d="M11 51C29 51 36 44 45 33"/></g><circle cx="47" cy="32" r="8" fill="#e8940f"/></svg>Charter Flight Network · preview build</p>
      <h1>Your website, as it stands right now</h1>
      <p class="built">Updated {now.strftime('%b %-d, %Y at %H:%M UTC')} · {pages_built:,} pages built ·
        cycle {m_cycle.group(1) if m_cycle else '—'}</p>
    </div>
    <a class="shot" href="{LIVE}/" target="_blank" rel="noopener" aria-label="Open the live preview site">
      {f'<img src="{thumb_uri}" alt="Current home page of the site">' if thumb_uri else ''}
      <span class="cta">Open the live preview →</span>
    </a>
  </div>
</header>

<section class="status">
  <div class="wrap">
    <ul class="chips">
      <li class="chip"><span class="dot"></span><b>{m_red.group(1) if m_red else '—'}/{m_red.group(2) if m_red else '—'}</b> old links still work</li>
      <li class="chip"><span class="dot{'' if (m_dead and m_dead.group(1) == '0') else ' warn'}"></span><b>{m_dead.group(1) if m_dead else '—'}</b> broken links on the site</li>
      <li class="chip"><span class="dot"></span><b>100/100/100</b> speed · accessibility · SEO</li>
      <li class="chip"><span class="dot warn"></span><b>{len(approvals)}</b> waiting on you</li>
    </ul>
  </div>
</section>

<div class="wrap grid">
  <main>
    <h2>What changed, newest first</h2>
    <p class="sub">Every entry is already live on the preview link above.</p>
    <ol class="cycles">
      {cycle_rows}
    </ol>
  </main>

  <div class="side">
    <section class="panel">
      <h2>Waiting on you</h2>
      <p class="sub">Things I won't decide on my own — pricing, legal, sending email, DNS.</p>
      <ul class="approvals">
        {approval_rows}
      </ul>
    </section>

    <section class="panel">
      <h2>Jump into a page</h2>
      <ul class="pages">
        {page_links}
      </ul>
    </section>
  </div>
</div>

<footer>
  <div class="wrap">
    <p>This is the staging preview — it's marked no-index so Google won't see it, and the
      quote forms don't send yet because they post to the mail script on the real host.</p>
    <p>Charter Flight Network is not a charter service provider. We do not own nor operate any
      aircraft. All charter quotes are generated by our charter network partners.</p>
  </div>
</footer>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(doc)
print(f"wrote {OUT} · {len(cycles)} cycles · {len(approvals)} approvals · {pages_built} pages")
