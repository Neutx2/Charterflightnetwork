#!/usr/bin/env python3
"""Sunrise / horizon studies: the aircraft climbs out from BEHIND the wordmark
and the trajectory reads as a sun or a horizon rather than a swoosh.

Two things had to change structurally for this to work at all:

1. Paint order. The artwork SVG is absolutely positioned and the type is
   static, so positioned content painted ON TOP of the letters. The type span
   now carries position:relative, which puts it later in the same stacking
   context and lets it occlude the art. That is what makes "behind" possible.

2. Contrast. Orange behind white type would wreck legibility where they
   overlap, so every variant here is drawn so the *visible* part of the sun
   sits above the cap height — the wordmark hides the disc's body and only its
   upper limb shows. Nothing orange ends up under a letter.

The artboard maps 0.025em per unit, with the wordmark's cap-top landing at
y=48, so anything above y=48 is visible and anything below is occluded.
"""
import base64
import pathlib

FONT = base64.b64encode(
    pathlib.Path('public/fonts/outfit-latin-wght-normal.woff2').read_bytes()
).decode()

O = '#ff7d02'
DIM = '#c85f00'
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3'
         'l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6'
         'l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z')
plane = lambda t, f=O: f'<g transform="{t} translate(-32 -32)" fill="{f}"><path d="{PLANE}"/></g>'

VB = '0 0 460 120'
PLACE = 'left:-.06em;top:-1.2em;height:3em;width:11.5em'

# Cap-top of the wordmark measured empirically at y=105 in artboard units
# (calibration render with guide lines). Every sun below is solved against it:
# r = (halfwidth^2 + d^2) / 2d, so the disc's visible slice above the letters
# is a chosen height and width rather than a guess.
V = [
    ('1', 'Rising sun', 'broad shallow disc behind “Charterflight”, aircraft climbing out of it',
     f'<circle cx="123" cy="210" r="120" fill="{O}"/>'
     + plane('translate(236 96) rotate(38) scale(.62)')),

    ('2', 'Sun and contrail', 'a dashed trail leaves the sun and lifts the aircraft clear',
     f'<circle cx="112" cy="210" r="120" fill="{O}"/>'
     f'<path d="M150 92C186 74 216 70 244 76" stroke="{O}" stroke-width="4" stroke-linecap="round"'
     f' stroke-dasharray="1.5 6" fill="none"/>'
     + plane('translate(262 68) rotate(44) scale(.58)')),

    ('3', 'Small sun', 'a tighter disc, more literally a sun',
     f'<circle cx="118" cy="165" r="71" fill="{O}"/>'
     + plane('translate(240 94) rotate(38) scale(.62)')),

    ('4', 'Sun on a horizon', 'the disc rising on a flat horizon that runs the full width',
     f'<circle cx="118" cy="174" r="83" fill="{O}"/>'
     f'<path d="M2 99h30M204 99h20M300 99h156" stroke="{O}" stroke-width="4.5" stroke-linecap="round"/>'
     + plane('translate(258 92) rotate(38) scale(.6)')),

    ('5', 'Wide horizon, no disc', 'just the curve of the earth behind the word',
     f'<path d="M-16 132C90 74 370 74 476 132" stroke="{O}" stroke-width="6" stroke-linecap="round" fill="none"/>'
     + plane('translate(240 92) rotate(38) scale(.62)')),

    ('6', 'Sunburst', 'disc with short rays breaking above the letters',
     f'<circle cx="118" cy="174" r="83" fill="{O}"/>'
     f'<g stroke="{O}" stroke-width="4" stroke-linecap="round">'
     f'<path d="M118 84v-11"/><path d="M74 90l-4-10"/><path d="M162 90l4-10"/>'
     f'<path d="M36 99l-9-7"/><path d="M200 99l9-7"/></g>'
     + plane('translate(252 92) rotate(38) scale(.6)')),

    ('7', 'Aircraft crossing the sun', 'the aircraft cuts across the disc\'s face',
     f'<circle cx="236" cy="210" r="120" fill="{O}"/>'
     + plane('translate(236 94) rotate(38) scale(.66)', DIM)),

    ('8', 'Low sun, aircraft high', 'the sun barely risen, the aircraft well up and away',
     f'<circle cx="112" cy="218" r="132" fill="{O}"/>'
     + plane('translate(288 60) rotate(40) scale(.6)')),
]


def lockup(art, px, tag):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    return (f'<span class="lk" style="font-size:{px}px">'
            f'<svg style="position:absolute;pointer-events:none;{PLACE}" viewBox="{VB}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>'
            f'<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>'
            f'{tg}</span>')


cards = ''.join(f'''<section class="card">
  <header><span class="num">{n}</span><b>{label}</b><span class="ds">{note}</span></header>
  <div class="panes"><div class="pane dark">{lockup(art,17,True)}{lockup(art,34,False)}</div>
  <div class="pane light">{lockup(art,17,True)}{lockup(art,26,False)}</div></div></section>'''
    for n, label, note, art in V)

HTML = f'''<title>Sunrise studies</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:28px 20px 56px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 26px Outfit;letter-spacing:-.6px;margin:0 0 6px}}
.lede{{color:#8fb0c8;font:400 15px system-ui;margin:0 0 24px;max-width:72ch;line-height:1.55}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:11px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 14px Outfit;min-width:26px;height:26px;padding:0 6px;border-radius:7px;display:grid;place-items:center;flex:none}}
.card header b{{font:700 15px Outfit}}.ds{{color:#8fb0c8;font:400 13px system-ui}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:26px 22px;display:flex;align-items:center;gap:38px;flex-wrap:wrap;min-height:132px}}
.dark{{background:#12314a}}.light{{background:#faf8f4}}
.lk{{position:relative;display:block;flex:none;line-height:1.12;padding-top:1.05em}}
/* the type must paint OVER the artwork — this is what puts the aircraft behind */
.wm{{position:relative;display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm em{{font-style:normal;color:{O}}}
.tag{{position:relative;display:block;font:400 11px system-ui;white-space:nowrap;margin-top:1px}}
.dark .wm{{color:#fff}}.dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}}.light .tag,.light .dom{{color:#5b7185}}.light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
</style>
<div class="wrap">
<h1>Sunrise studies</h1>
<p class="lede">The aircraft climbs out from behind “Charterflight”, and the trajectory reads as a sun or a horizon. In every one the disc's body is hidden by the type — only its upper limb shows — so no orange ends up behind a white letter.</p>
{cards}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/sunrise.html')
out.write_text(HTML)
print(f'wrote {out} — {len(V)} studies, {len(HTML)//1024} KB')
