#!/usr/bin/env python3
"""Build the brand decision page: the research, the rejected candidates, and
every option in one numbered list.

Run from the repo root:
    python3 scripts/render_brand_decision.py

Everything on the page is generated from the real sources, so it cannot drift
from what would actually ship:
  · logotypes 1-8   parsed out of src/lib/wordmark-arcs.ts (the shipped data)
  · logotypes 9-18  imported from scripts/render_logo_options.py
  · icons A-F       defined below, the same paths tested at true device pixels
  · evidence images read from src/assets/legacy/ and embedded as data URIs
"""
import base64
import io
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import render_logo_options as r2  # noqa: E402  (also writes its own page; harmless)

from PIL import Image  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
O, TEAL, WHITE = '#ff7d02', '#1c5b6a', '#faf8f4'

FONT = base64.b64encode((ROOT / 'public/fonts/outfit-latin-wght-normal.woff2').read_bytes()).decode()


def img_uri(path: str, width: int, crop=None, quality=72) -> str:
    im = Image.open(ROOT / path).convert('RGB')
    if crop:
        im = im.crop(crop)
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=quality)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- icons
def plane(t, fill=O):
    return f'<g transform="{t} translate(-32 -32)" fill="{fill}"><path d="{r2.PLANE}"/></g>'


tile = lambda c: f'<rect width="64" height="64" rx="15" fill="{c}"/>'

ICONS = [
    ('A', 'Aircraft + three contrails', 'SHIPPED — one request, up to three quotes',
     tile(TEAL)
     + f'<g stroke="{WHITE}" stroke-width="5" stroke-linecap="round" opacity=".85">'
       f'<path d="M8 50h12"/><path d="M8 36h10"/><path d="M11 22h8"/></g>'
     + plane('translate(39 29) rotate(40) scale(1.06)')),
    ('B', 'Aircraft alone', 'legible, but the most crowded idea in the peer set',
     tile(TEAL) + plane('translate(32 32) rotate(38) scale(1.28)')),
    ('C', 'Three routes', 'the network idea, no aircraft — distinctive but abstract',
     tile(TEAL)
     + f'<g fill="none" stroke="{O}" stroke-linecap="round" stroke-width="7">'
       f'<path d="M12 15C28 15 34 21 42 31"/><path d="M12 32h30"/>'
       f'<path d="M12 49C28 49 34 43 42 33"/></g>'
       f'<circle cx="46" cy="32" r="8.5" fill="{WHITE}"/>'),
    ('D', 'Tapered C', 'reads best of all at 16px — but see Chartright below',
     tile(TEAL) + f'<path d="M46 17A21 21 0 1 0 45 49L40.5 41.5A13 13 0 1 1 41.5 24Z" fill="{O}"/>'),
    ('E', 'C + aircraft', 'same problem as D',
     tile(TEAL) + f'<path d="M46 17A21 21 0 1 0 45 49L40.5 41.5A13 13 0 1 1 41.5 24Z" fill="{O}"/>'
     + plane('translate(52 13) rotate(40) scale(.5)')),
    ('F', 'Classic swoosh in a tile', 'the OLD favicon — fails at 16px',
     tile(TEAL)
     + f'<path d="M9 21C14 40 32 45 47 32" stroke="{O}" stroke-width="4.8" '
       f'stroke-linecap="round" fill="none"/>'
     + plane('translate(45 20) rotate(38) scale(.54)')),
]


# ------------------------------------------------- logotypes, round 1 (from TS)
def parse_round1():
    ts = (ROOT / 'src/lib/wordmark-arcs.ts').read_text()
    out = []
    pat = (r"^  '?([a-z-]+)'?: \{\n    label: '([^']+)',\n    note: '([^']+)',\n"
           r"    viewBox: '([^']+)',\n    place: '([^']+)',\n(    under: true,\n)?    paths: `([^`]+)`,")
    for m in re.finditer(pat, ts, re.M):
        key, label, note, vb, place, under, paths = m.groups()
        paths = re.sub(r"\$\{plane\('([^']+)'\)\}", lambda mm: plane(mm.group(1)),
                       paths.replace('${O}', O))
        out.append(dict(key=key, label=label, note=note, vb=vb, place=place,
                        under=bool(under), paths=paths, word=r2.CLOSED))
    return out


CLOSED = r2.CLOSED


def lockup(v, px, tag):
    under = v.get('under')
    pad = ('padding-bottom:1.5em' if not tag else '') if under else (
        'padding-top:.72em' if 'arc' in v or 'place' in v else '')
    mt = '1.5em' if under else '1px'
    art = ''
    place = v.get('place') or (v.get('arc') or {}).get('place')
    if place:
        a = v.get('arc') or v
        art = (f'<svg style="position:absolute;pointer-events:none;{a["place"]}" '
               f'viewBox="{a["viewBox" if "viewBox" in a else "vb"]}" '
               f'preserveAspectRatio="xMinYMid meet">{a["paths"]}</svg>')
    tg = (f'<span class="tag" style="margin-top:{mt}">Canadian owned &amp; operated since 2008</span>'
          if tag else '')
    if 'mark' in v:
        return (f'<span class="row" style="font-size:{px}px">{v["mark"]}'
                f'<span class="lk">{v["word"]}{tg}</span></span>')
    return f'<span class="lk" style="font-size:{px}px;{pad}">{art}{v["word"]}{tg}</span>'


def card(num, label, note, key, body_dark, body_light):
    tag = f'<code>{key}</code>' if key else ''
    return f'''<section class="card">
  <header><span class="num">{num}</span><b>{label}</b><span class="ds">{note}</span>{tag}</header>
  <div class="panes"><div class="pane dark">{body_dark}</div>
  <div class="pane light">{body_light}</div></div></section>'''


round1 = parse_round1()
logo_cards = []
for i, v in enumerate(round1, 1):
    logo_cards.append(card(i, v['label'], v['note'], v['key'],
                           lockup(v, 17, True) + lockup(v, 32, False),
                           lockup(v, 17, True) + lockup(v, 26, False)))
for v in r2.VARIANTS:
    logo_cards.append(card(v['n'], v['label'], v['note'], v['key'],
                           r2.lockup(v, 17, True) + r2.lockup(v, 32, False),
                           r2.lockup(v, 17, True) + r2.lockup(v, 26, False)))

icon_cards = []
for letter, label, note, body in ICONS:
    sizes = lambda: ''.join(
        f'<svg width="{s}" height="{s}" viewBox="0 0 64 64">{body}</svg>' for s in (16, 20, 24, 32, 48, 72))
    icon_cards.append(card(letter, label, note, '',
                           f'<span class="icons">{sizes()}</span>',
                           f'<span class="icons">{sizes()}</span>'))

PEER_ON = img_uri('src/assets/legacy/CFN_Images/Air_Charter_650/air_charter_logos/Air-charter-Logos-650-Ontario.jpg', 430)
PEER_MB = img_uri('src/assets/legacy/CFN_Images/Air_Charter_650/air_charter_logos/Air-charter-Logos-650-Manitoba-Sk.jpg', 430)
CHARTRIGHT = img_uri('src/assets/legacy/CFN_Images/Air_Charter_650/air_charter_logos/Air-charter-Logos-650-Ontario.jpg', 420, crop=(8, 362, 320, 478), quality=88)
CLASSIC = img_uri('src/assets/legacy/Logo_green_white.jpg', 520, quality=88)

HTML = f'''<title>Charter Flight Network — brand decision</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:30px 20px 64px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 30px Outfit;letter-spacing:-.8px;margin:0 0 8px}}
h2{{font:800 20px Outfit;letter-spacing:-.4px;margin:44px 0 6px;padding-top:16px;border-top:1px solid #ffffff1a}}
h3{{font:700 15px Outfit;margin:24px 0 6px;color:#ffd9b0}}
p{{color:#a8c4d8;font:400 15px system-ui;line-height:1.62;margin:0 0 12px;max-width:74ch}}
.lede{{font-size:16px;color:#8fb0c8}}
.evid{{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0 6px}}
.evid figure{{margin:0;background:#101f30;border:1px solid #ffffff16;border-radius:12px;padding:12px;max-width:462px}}
.evid img{{display:block;width:100%;border-radius:6px}}
.evid figcaption{{color:#7fa3bd;font:400 12.5px system-ui;margin-top:9px;line-height:1.5}}
.verdict{{background:#12314a;border-left:3px solid {O};border-radius:0 10px 10px 0;padding:12px 16px;margin:14px 0}}
.verdict b{{color:{O}}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:11px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 14px Outfit;min-width:26px;height:26px;padding:0 6px;border-radius:7px;display:grid;place-items:center;flex:none}}
.card header b{{font:700 15px Outfit;letter-spacing:-.2px}}
.ds{{color:#8fb0c8;font:400 13px system-ui}}
code{{color:#6f93ad;font:500 12px ui-monospace,monospace;background:#0b1a28;padding:3px 8px;border-radius:5px}}
.card header code{{margin-left:auto}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:20px;display:flex;align-items:center;gap:30px;flex-wrap:wrap;min-height:104px}}
.dark{{background:#12314a}} .light{{background:{WHITE}}}
.icons{{display:flex;align-items:flex-end;gap:14px}}
.lk{{position:relative;line-height:1.12;display:block;flex:none}}
.lk svg{{position:absolute;pointer-events:none}}
.row{{display:flex;align-items:center;gap:.55em;flex:none}}
.badge{{width:2.5em;height:2.5em;flex:none}}
.wm{{display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm .lt{{font-weight:300;letter-spacing:-.01em}}
.tag{{display:block;font:400 11px system-ui;white-space:nowrap}}
.dark .wm{{color:#fff}} .dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}} .light .tag,.light .dom{{color:#5b7185}}
.wm em{{font-style:normal;color:{O}}} .light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
.how{{background:#101f30;border:1px solid #ffffff16;border-radius:12px;padding:16px 20px;margin-top:20px}}
.how p{{margin-bottom:0}}
</style>
<div class="wrap">
<h1>Brand decision</h1>
<p class="lede">The evidence behind the current mark, the candidates it beat, and every option in one numbered list. Pick by number or letter — logotypes are numbered 1–18, icons are lettered A–F. They are independent choices: you can take a logotype from one row and an icon from another.</p>

<h2>What the research found</h2>

<h3>1. The old icon failed the only test that matters</h3>
<p>A favicon is only ever seen at 16–32 pixels. Rendered at a true 16 device pixels, the previous mark was an orange smudge with a speck — the swoosh was a hairline and the aircraft about five pixels of detail. Standard scalability guidance is blunt about this: thin strokes vanish, and the test is to shrink the mark until it is a few pixels across and see whether it survives. Compare <b>F</b> against <b>A</b> in the list below at the 16px size.</p>

<h3>2. CFN is not an operator, and its directory proves it</h3>
<div class="evid">
  <figure><img src="{PEER_ON}"><figcaption>Ontario operators, from the legacy site's own asset folder</figcaption></figure>
  <figure><img src="{PEER_MB}"><figcaption>Manitoba and Saskatchewan operators, same source</figcaption></figure>
</div>
<p>These are pages CFN itself published. The peer set is saturated with aircraft, wings, birds, feathers, sun discs and heritage roundels — and the directory renders 530 of these logos <em>beside</em> CFN's own. Charter Flight Network is not a charter operator; it is the network above them. An intermediary needs an identity distinct from its suppliers, because the customer's relationship is with the platform, not the supplier.</p>

<h3>3. The best small-size candidate had to be killed</h3>
<div class="evid">
  <figure><img src="{CHARTRIGHT}"><figcaption>Chartright Air Group — an operator listed in CFN's own directory</figcaption></figure>
</div>
<p>A tapered <b>C</b> read better at 16px than anything else tested, and doubled as the initial of Charterflight. Then this turned up in the operator sheets: a bold C on a dark square, belonging to a company CFN lists. A broker whose mark echoes one of its own listed operators reads as derivative at best and as implying affiliation at worst. Options <b>D</b> and <b>E</b> below are the candidates this ruled out — they are still shown so you can judge the call yourself.</p>

<h3>4. The luxury convention is the wrong register</h3>
<p>Jet-broker branding trends to silver, black and hairline type for high-net-worth flyers. CFN's audience is fishermen, lodge guests, mining crews and remote communities. Borrowing that register would misrepresent the business.</p>

<h3>5. Heritage is an asset, not a constraint</h3>
<div class="evid">
  <figure style="max-width:560px"><img src="{CLASSIC}"><figcaption>The 2008 logo. Both brand colours are sampled from this file — #ff7d02 and #1c5b6a — rather than chosen.</figcaption></figure>
</div>
<p>Eighteen years of recognition sit in the orange, the swoosh and the closed-up two-tone wordmark. Every logotype below keeps all three.</p>

<div class="verdict"><p><b>Conclusion.</b> Keep the classic logotype; replace the icon with something purpose-built for small sizes that reads as the network rather than as another operator. What shipped is an aircraft — which is what the business is about — trailed by three contrails, which is what only this business does: one request, up to three competitive quotes. The trails are white because at 16px orange-on-orange merges into the fuselage and the mark collapses.</p></div>

<h2>Icons — pick a letter</h2>
<p>Shown at 16, 20, 24, 32, 48 and 72 pixels, which is the range a favicon and app icon actually live in. Judge these at the small end, not the large one.</p>
{''.join(icon_cards)}

<h2>Logotypes — pick a number</h2>
<p>Shown at the real header size (17px) and large, on the site's navy and on warm white. Number 1 is what is live now.</p>
{''.join(logo_cards)}

<div class="how">
<p><b>How this page was made.</b> Nothing here is a mock-up. Logotypes 1–8 are parsed out of <code>src/lib/wordmark-arcs.ts</code>, the file the site actually renders from; 9–18 come from <code>scripts/render_logo_options.py</code>; the icons are the same paths tested at true device pixels; and the evidence images are read straight from <code>src/assets/legacy/</code>. Regenerate with <code>python3 scripts/render_brand_decision.py</code>.</p>
</div>
</div>'''

out = ROOT / '.brand-decision.html'
if len(sys.argv) > 1:
    out = pathlib.Path(sys.argv[1])
out.write_text(HTML)
print(f'wrote {out} — {len(HTML)//1024} KB, {len(logo_cards)} logotypes, {len(icon_cards)} icons')
