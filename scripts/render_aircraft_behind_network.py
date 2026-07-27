#!/usr/bin/env python3
"""Aircraft behind "Network", sized against that word rather than by eye.

Measured in the browser, in artboard units (0.025em per unit):
    "Network"  spans x 237 -> 390, so 153 units wide, centred on x = 313
    cap line   y = 105
    aircraft   rotated 38 deg, its bounding box is ~60 units at scale 1

So "about 2/3 the size of Network" resolves to:
    target width = 153 x 2/3 = 102 units  ->  scale = 102 / 60 = 1.7

1.4 and 2.0 are shown either side of it. The aircraft sits at x=313 — the
centre of "Network" — with its belly below the cap line so the letters occlude
it and it reads as climbing out from behind the word.
"""
import base64
import pathlib

FONT = base64.b64encode(
    pathlib.Path('public/fonts/outfit-latin-wght-normal.woff2').read_bytes()
).decode()

O = '#ff7d02'
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3'
         'l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6'
         'l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z')
plane = lambda t: f'<g transform="{t} translate(-32 -32)" fill="{O}"><path d="{PLANE}"/></g>'

VB = '0 -60 460 180'
PLACE = 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em'

SUN = f'<circle cx="118" cy="165" r="71" fill="{O}"/>'
HORIZON = (f'<path d="M-16 132C90 74 370 74 476 132" stroke="{O}" stroke-width="6"'
           f' stroke-linecap="round" fill="none"/>')

NET_CX = 313          # centre of the word "Network"
CAP = 105             # cap line

# (label, scale, centre y, note) — deeper tuck for larger aircraft so the
# amount showing above the letters stays sane
# Keeping the SAME FRACTION of the aircraft visible as it grows means the
# centre must rise, not sink. Visible height above the cap line is
# 105 - (cy - 30*scale); setting that to 65% of the aircraft's 60*scale height
# gives cy = 105 - 9*scale. A fixed or sinking centre buries the fuselage and
# what is left stops reading as an aircraft at all — which is exactly what the
# first pass did at 1.7 and 2.0.
STEPS = [
    ('1.4', 1.40, 92, '≈ 55% of “Network”'),
    ('1.7', 1.70, 90, '≈ 2/3 of “Network” — as asked'),
    ('2.0', 2.00, 87, '≈ 78% of “Network”'),
]


def lockup(art, px, tag):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    return (f'<span class="lk" style="font-size:{px}px">'
            f'<svg style="position:absolute;pointer-events:none;{PLACE}" viewBox="{VB}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>'
            f'<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>'
            f'{tg}</span>')


sections = ''
for name, base, key in [('Small sun', SUN, 'sun'), ('Wide horizon', HORIZON, 'hz')]:
    cards = ''
    for label, sc, cy, note in STEPS:
        art = base + plane(f'translate({NET_CX} {cy}) rotate(38) scale({sc})')
        width = round(60 * sc)
        pct = round(width / 153 * 100)
        cards += f'''<section class="card">
  <header><span class="num">{key}-{label}</span><b>scale {label}</b><span class="ds">{note}</span>
  <code>{width}u wide · {pct}% of “Network”</code></header>
  <div class="panes"><div class="pane dark">{lockup(art,17,True)}{lockup(art,34,False)}</div>
  <div class="pane light">{lockup(art,17,True)}{lockup(art,26,False)}</div></div>
  <div class="bar"><span class="barlab">in a real 64px header</span>{lockup(art,17,True)}</div></section>'''
    sections += f'<h2>{name}</h2>{cards}'

HTML = f'''<title>Aircraft behind Network</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:28px 20px 56px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 26px Outfit;letter-spacing:-.6px;margin:0 0 6px}}
h2{{font:800 19px Outfit;margin:34px 0 12px;padding-top:14px;border-top:1px solid #ffffff1a}}
.lede{{color:#8fb0c8;font:400 15px system-ui;margin:0 0 10px;max-width:74ch;line-height:1.55}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:11px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 12px ui-monospace,monospace;padding:5px 9px;border-radius:7px;flex:none}}
.card header b{{font:700 15px Outfit}}.ds{{color:#8fb0c8;font:400 13px system-ui}}
code{{margin-left:auto;color:#6f93ad;font:500 12px ui-monospace,monospace;background:#0b1a28;padding:4px 9px;border-radius:5px}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:30px 22px;display:flex;align-items:center;gap:38px;flex-wrap:wrap;min-height:150px}}
.dark{{background:#12314a}}.light{{background:#faf8f4}}
.lk{{position:relative;display:block;flex:none;line-height:1.12;padding-top:1.6em}}
.wm{{position:relative;display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm em{{font-style:normal;color:{O}}}
.tag{{position:relative;display:block;font:400 11px system-ui;white-space:nowrap;margin-top:1px}}
.dark .wm{{color:#fff}}.dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}}.light .tag,.light .dom{{color:#5b7185}}.light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
.bar{{height:64px;background:#0b2033;display:flex;align-items:center;gap:20px;padding:0 18px;overflow:hidden}}
.barlab{{font:600 11px system-ui;color:#7fa3bd;flex:none}}
.bar .wm{{color:#fff}} .bar .tag,.bar .dom{{color:#b3d1e7}}
</style>
<div class="wrap">
<h1>Aircraft behind “Network”</h1>
<p class="lede">Sized against the word rather than by eye. “Network” measures 153 artboard units wide; the aircraft's rotated bounding box is about 60 units at scale 1, so two-thirds of the word lands at <b>scale 1.7</b>. One step either side for comparison. Each is also shown inside a real 64px header.</p>
{sections}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/network.html')
out.write_text(HTML)
print(f'wrote {out} — {len(STEPS)*2} renders, {len(HTML)//1024} KB')
