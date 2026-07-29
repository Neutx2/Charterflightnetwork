#!/usr/bin/env python3
"""Taper & echo family: everything here descends from the two picks —
25 (tapered horizon) and 28 (echo line). Numbering continues at 37.

Same calibrated artboard throughout. The echo curve's dots in the pearl
variants are computed points on the echo cubic with radii that shrink
toward the ends, so the echo fades the same way the taper does.
"""
import base64
import pathlib

ROOT = pathlib.Path('/home/user/Charterflightnetwork')
FONT = base64.b64encode((ROOT / 'public/fonts/outfit-latin-wght-normal.woff2').read_bytes()).decode()

O = '#ff7d02'
TEAL = '#2d7b8c'
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3'
         'l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6'
         'l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z')
plane = lambda t: f'<g transform="{t} translate(-32 -32)" fill="{O}"><path d="{PLANE}"/></g>'

VB = '0 -60 460 180'
PLACE = 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em'
AC = plane('translate(368 84) rotate(38) scale(1.7)')

TAPER = f'<path d="M-16 132C90 68 370 68 476 132C370 80 90 80 -16 132Z" fill="{TEAL}"/>'
ECHO = (f'<path d="M6 143C104 87 356 87 454 143" stroke="{TEAL}" stroke-width="3.4"'
        f' stroke-linecap="round" stroke-dasharray="2 7" opacity=".55" fill="none"/>')


def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def pearls(color=TEAL, opacity=.6):
    """Dots along the echo cubic, shrinking toward the ends."""
    p0, p1, p2, p3 = (6, 143), (104, 87), (356, 87), (454, 143)
    out = []
    n = 15
    for i in range(n):
        t = 0.08 + (0.84 * i) / (n - 1)
        x, y = cubic(p0, p1, p2, p3, t)
        r = 2.7 * (1 - abs(t - 0.5) * 1.55)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>')
    return f'<g fill="{color}" opacity="{opacity}">{"".join(out)}</g>'


# Right half of the main taper curve (de Casteljau split at t=0.5), warmed
# to orange and fading to nothing at both of its own ends — 25 and 26 merged.
SUNLIT = f'<path d="M230 84C326.5 84 423 100 476 132C423 106 326.5 90 230 84Z" fill="{O}"/>'

CARDS = [
    ('37', 'Taper + echo', 'your two picks, together verbatim', TAPER + ECHO + AC, False),
    ('38', 'Twin tapers', 'the echo is a second, thinner tapered lens — both lines fade at the ends',
     TAPER + f'<path d="M6 143C104 84 356 84 454 143C356 90 104 90 6 143Z" fill="{TEAL}" opacity=".55"/>' + AC, False),
    ('39', 'Pearl echo', 'the echo as dots that shrink toward the ends — fades the way the taper does',
     TAPER + pearls() + AC, False),
    ('40', 'Dotted echo', 'soft round dots, evenly sized',
     TAPER + f'<path d="M6 143C104 87 356 87 454 143" stroke="{TEAL}" stroke-width="3.6"'
     f' stroke-linecap="round" stroke-dasharray="0 10" opacity=".6" fill="none"/>' + AC, False),
    ('41', 'Sunlit taper', 'the taper warms to orange under the aircraft — 25 and 26 merged',
     TAPER + SUNLIT + ECHO + AC, False),
    ('42', 'Orange echo', 'teal taper, the echo dashed in orange',
     TAPER + f'<path d="M6 143C104 87 356 87 454 143" stroke="{O}" stroke-width="3"'
     f' stroke-linecap="round" stroke-dasharray="2 7" opacity=".7" fill="none"/>' + AC, False),
    ('43', 'Triple echo', 'two echoes fading in turn — contour lines of the sky',
     TAPER + ECHO + f'<path d="M18 152C116 98 344 98 442 152" stroke="{TEAL}" stroke-width="2.6"'
     f' stroke-linecap="round" stroke-dasharray="2 8" opacity=".32" fill="none"/>' + AC, False),
    ('44', 'The refined pair', 'taper + pearl echo + type harmony — my combined pick',
     TAPER + pearls() + AC, True),
]


def lockup(art, px, tag):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    return (f'<span class="lk" style="font-size:{px}px">'
            f'<svg style="position:absolute;pointer-events:none;{PLACE}" viewBox="{VB}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>'
            f'<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>'
            f'{tg}</span>')


def card(n, name, note, art, harmony):
    h = ' harmony' if harmony else ''
    return f'''<section class="card{h}">
  <header><span class="num">{n}</span><b>{name}</b><span class="ds">{note}</span></header>
  <div class="panes"><div class="pane dark">{lockup(art,17,True)}{lockup(art,34,False)}</div>
  <div class="pane light">{lockup(art,17,True)}{lockup(art,26,False)}</div></div>
  <div class="bar"><span class="barlab">on the real website header</span>{lockup(art,17,True)}</div></section>'''


refs = (f'<div class="fam" data-shot><h2><span class="famkey">✓</span>The two picks'
        f' <small>— 25 and 28, unchanged, for reference</small></h2>'
        + card('25', 'Tapered horizon', 'the line swells at the centre, fades at the ends', TAPER + AC, False)
        + card('28', 'Echo line', 'a faint dashed second line',
               f'<path d="M-16 132C90 74 370 74 476 132" stroke="{TEAL}" stroke-width="6"'
               f' stroke-linecap="round" fill="none"/>' + ECHO + AC, False)
        + '</div>')

half = len(CARDS) // 2
sections = refs
for title, chunk in [('Combinations', CARDS[:half]), ('Further', CARDS[half:])]:
    sections += f'<div class="fam" data-shot><h2><span class="famkey">+</span>{title}</h2>'
    for c in chunk:
        sections += card(*c)
    sections += '</div>'

HTML = f'''<title>Taper &amp; echo — 37 to 44</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:30px 20px 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 28px Outfit;letter-spacing:-.6px;margin:0 0 8px}}
h2{{font:800 21px Outfit;margin:0 0 14px;display:flex;align-items:center;gap:10px}}
h2 small{{font:400 15px system-ui;color:#8fb0c8}}
.famkey{{background:#ffffff14;border:1px solid #ffffff2a;color:#ffb36b;font:800 14px Outfit;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;flex:none}}
.lede{{color:#9db9cf;font:400 16px system-ui;margin:0 0 26px;max-width:76ch;line-height:1.6}}
.fam{{margin-top:34px;padding-top:20px;border-top:1px solid #ffffff1a}}
.fam:first-child{{margin-top:0;padding-top:0;border-top:0}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:13px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 16px Outfit;min-width:34px;height:30px;padding:0 8px;border-radius:8px;display:grid;place-items:center;flex:none}}
.card header b{{font:700 16px Outfit}}.ds{{color:#8fb0c8;font:400 14px system-ui}}
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
.harmony .dark .dom,.harmony .dark .tag,.harmony .bar .dom,.harmony .bar .tag{{color:#5f9db0}}
.harmony .light .dom,.harmony .light .tag{{color:#1c5b6a}}
.bar{{height:64px;background:#0b2033;display:flex;align-items:center;gap:20px;padding:0 18px;overflow:hidden}}
.barlab{{font:600 12px system-ui;color:#7fa3bd;flex:none}}
.bar .wm{{color:#fff}} .bar .tag,.bar .dom{{color:#b3d1e7}}
</style>
<div class="wrap">
<h1>Taper &amp; echo</h1>
<p class="lede">Everything here descends from your two picks: the <b>tapered horizon (25)</b> and the <b>echo line (28)</b>. First together as-is, then the echo re-drawn in different voices, and colour brought into the taper. Say the number.</p>
{sections}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/taperecho.html')
out.write_text(HTML)
print(f'wrote {out}, {len(HTML)//1024} KB')
