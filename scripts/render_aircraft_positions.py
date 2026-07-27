#!/usr/bin/env python3
"""Aircraft positioning study on logotype A (classic-climb).

The arc, the dashed contrail and the type are IDENTICAL in every option — the
only thing that moves is the aircraft's transform. That is the whole point:
isolate one variable.

Note on the artboard: A's viewBox was 0 0 200 56 and the aircraft sat at y=6,
so its upper wingtip was actually being clipped by the SVG viewport. The
viewBox here is 0 -16 200 72 with the placement recomputed so the arc renders
at exactly the same size and position — 0.023em per unit, viewBox y=0 landing
at -0.214em — which buys headroom without changing what A looks like.
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

# A's arc and contrail, byte for byte. Never varies.
ARC = (f'<path d="M4 42C32 6 96 2 136 24" stroke="{O}" stroke-width="7.5" stroke-linecap="round" fill="none"/>'
       f'<path d="M16 46C42 18 96 14 132 32" stroke="{O}" stroke-width="4.5" stroke-linecap="round"'
       f' stroke-dasharray="2 7" fill="none"/>')

VB = '0 -16 200 72'
PLACE = 'left:.02em;top:-.582em;height:1.656em;width:4.6em'

# (label, note, transform) — only this changes
POSITIONS = [
    ('1', 'As now', 'right end, just above the arc tip', 'translate(152 6) rotate(34) scale(.86)'),
    ('2', 'Higher and further out', 'more sky between aircraft and word', 'translate(166 -6) rotate(34) scale(.86)'),
    ('3', 'At the apex', 'sitting on top of the arc, mid-word', 'translate(84 -4) rotate(16) scale(.82)'),
    ('4', 'Steeper climb-out', 'same place, pitched up hard', 'translate(150 2) rotate(54) scale(.88)'),
    ('5', 'Riding the tail', 'lower and tucked onto the arc\'s descent', 'translate(142 20) rotate(46) scale(.82)'),
    ('6', 'Large and close', 'aircraft dominant, arc supporting', 'translate(144 8) rotate(30) scale(1.12)'),
    ('7', 'Small and delicate', 'a light touch at the very tip', 'translate(154 6) rotate(34) scale(.62)'),
    ('8', 'Level, well clear', 'cruising out to the right, almost flat', 'translate(174 8) rotate(74) scale(.84)'),
    ('9', 'Departing left', 'at the start of the trail, the whole route ahead', 'translate(14 30) rotate(34) scale(.8)'),
    ('10', 'Crossing the word', 'pushed right, over “Network”', 'translate(188 14) rotate(26) scale(.8)'),
]

WORD = ('<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>')


def lockup(tf, px, tag):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    art = ARC + f'<g transform="{tf} translate(-32 -32)" fill="{O}"><path d="{PLANE}"/></g>'
    return (f'<span class="lk" style="font-size:{px}px;padding-top:.72em">'
            f'<svg style="position:absolute;pointer-events:none;{PLACE}" viewBox="{VB}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>{WORD}{tg}</span>')


cards = ''.join(f'''<section class="card">
  <header><span class="num">{n}</span><b>{label}</b><span class="ds">{note}</span></header>
  <div class="panes"><div class="pane dark">{lockup(tf,17,True)}{lockup(tf,36,False)}</div>
  <div class="pane light">{lockup(tf,17,True)}{lockup(tf,26,False)}</div></div></section>'''
    for n, label, note, tf in POSITIONS)

HTML = f'''<title>Aircraft positioning — logotype A</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:28px 20px 56px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 26px Outfit;letter-spacing:-.6px;margin:0 0 6px}}
.lede{{color:#8fb0c8;font:400 15px system-ui;margin:0 0 24px;max-width:70ch;line-height:1.55}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:11px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 14px Outfit;min-width:26px;height:26px;padding:0 6px;border-radius:7px;display:grid;place-items:center;flex:none}}
.card header b{{font:700 15px Outfit}}.ds{{color:#8fb0c8;font:400 13px system-ui}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:22px;display:flex;align-items:center;gap:34px;flex-wrap:wrap;min-height:120px}}
.dark{{background:#12314a}}.light{{background:#faf8f4}}
.lk{{position:relative;display:block;flex:none;line-height:1.12}}
.wm{{display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm em{{font-style:normal;color:{O}}}
.tag{{display:block;font:400 11px system-ui;white-space:nowrap;margin-top:1px}}
.dark .wm{{color:#fff}}.dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}}.light .tag,.light .dom{{color:#5b7185}}.light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
</style>
<div class="wrap">
<h1>Aircraft positioning — logotype A</h1>
<p class="lede">The arc, the dashed contrail and the type are identical in all ten. Only the aircraft moves. Number 1 is exactly what is live now. Shown at the real header size and large, on navy and warm white.</p>
{cards}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/positions.html')
out.write_text(HTML)
print(f'wrote {out} — {len(POSITIONS)} positions, {len(HTML)//1024} KB')
