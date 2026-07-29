#!/usr/bin/env python3
"""Refinement pass on the shipped logotype (option 24): teal horizon,
aircraft climbing out from behind the end of "Network". Numbering continues
at 25. One variable changes per card; 36 combines the winners.

Calibration unchanged: 0.025em/unit, cap y=105, "Network" x 237-390,
aircraft scale 1.7 at (368,84) rotate 38, viewport clips at y=120.
The horizon at the aircraft's x (~368) sits at y~99 (cubic at t=0.75).
"""
import base64
import pathlib

ROOT = pathlib.Path('/home/user/Charterflightnetwork')
FONT = base64.b64encode((ROOT / 'public/fonts/outfit-latin-wght-normal.woff2').read_bytes()).decode()

O = '#ff7d02'
OB = '#ff9424'            # ember-400, brighter
TEAL = '#2d7b8c'          # heritage-400 — shipped
TEAL_L = '#3e93a6'        # a step lighter
TEAL_D = '#1c5b6a'        # heritage-500, deeper
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3'
         'l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6'
         'l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z')
plane = lambda t, f=O: f'<g transform="{t} translate(-32 -32)" fill="{f}"><path d="{PLANE}"/></g>'
hz = lambda c, w=6: (f'<path d="M-16 132C90 74 370 74 476 132" stroke="{c}" stroke-width="{w}"'
                     f' stroke-linecap="round" fill="none"/>')

VB = '0 -60 460 180'
PLACE = 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em'
AC = plane('translate(368 84) rotate(38) scale(1.7)')

# Filled lens: the same curve doubled back, 9u thick at centre, tapering to
# nothing at both ends — a horizon that fades out instead of stopping.
TAPER = f'<path d="M-16 132C90 68 370 68 476 132C370 80 90 80 -16 132Z" fill="{TEAL}"/>'
# Orange segment laid over the horizon where the aircraft crosses it —
# the patch of line the sunrise catches. Follows the same cubic locally.
GLINT = f'<path d="M316 92C350 96 385 102 418 110" stroke="{O}" stroke-width="6" stroke-linecap="round" fill="none"/>'

# (num, name, note, art, harmony?)
CARDS = [
    ('A', 'The line', 'how the horizon itself is drawn'),
    ('25', 'Tapered horizon', 'the line swells at the centre and fades to nothing at the ends', TAPER + AC),
    ('26', 'Sunlit crossing', 'the stretch of horizon under the aircraft catches the light in orange', hz(TEAL) + GLINT + AC),
    ('27', 'Rising through', 'the horizon passes in FRONT of the aircraft\'s belly — it climbs from behind the line',
     AC.replace('</g>', '</g>') + hz(TEAL)),
    ('28', 'Echo line', 'a faint dashed second line below the horizon',
     hz(TEAL) + f'<path d="M6 143C104 87 356 87 454 143" stroke="{TEAL}" stroke-width="3.4"'
     f' stroke-linecap="round" stroke-dasharray="2 7" opacity=".55" fill="none"/>' + AC),

    ('B', 'Colour', 'shades of the line and the aircraft'),
    ('29', 'Lighter teal', 'the line a step brighter — more visible on navy', hz(TEAL_L) + AC),
    ('30', 'Deeper teal', 'the line a step darker — calmer still', hz(TEAL_D) + AC),
    ('31', 'Brighter aircraft', 'the aircraft in the warmer ember-400 orange', hz(TEAL) + plane('translate(368 84) rotate(38) scale(1.7)', OB)),

    ('C', 'The aircraft', 'attitude and tuck'),
    ('32', 'Steeper', 'pitched up to 46 degrees', hz(TEAL) + plane('translate(368 80) rotate(46) scale(1.7)')),
    ('33', 'Gentler', 'eased back to 30 degrees', hz(TEAL) + plane('translate(368 86) rotate(30) scale(1.7)')),
    ('34', 'Deeper tuck', 'moved a touch left and lower — more of it behind the letters',
     hz(TEAL) + plane('translate(352 90) rotate(38) scale(1.7)')),

    ('D', 'Type & the polished one', ''),
    ('35', 'Type harmony', 'same art; ".com" and the tagline take the horizon\'s teal', hz(TEAL) + AC, True),
    ('36', 'The polished one', 'tapered horizon + sunlit crossing + type harmony', TAPER + GLINT + AC, True),
]


def lockup(art, px, tag):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    return (f'<span class="lk" style="font-size:{px}px">'
            f'<svg style="position:absolute;pointer-events:none;{PLACE}" viewBox="{VB}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>'
            f'<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>'
            f'{tg}</span>')


def card(n, name, note, art, harmony=False):
    h = ' harmony' if harmony else ''
    return f'''<section class="card{h}">
  <header><span class="num">{n}</span><b>{name}</b><span class="ds">{note}</span></header>
  <div class="panes"><div class="pane dark">{lockup(art,17,True)}{lockup(art,34,False)}</div>
  <div class="pane light">{lockup(art,17,True)}{lockup(art,26,False)}</div></div>
  <div class="bar"><span class="barlab">on the real website header</span>{lockup(art,17,True)}</div></section>'''


sections = f'''<div class="fam" data-shot>
<h2><span class="famkey">✓</span>As shipped <small>— option 24, now live on the site</small></h2>
{card('24', 'Teal horizon climb-out', 'the baseline every card below varies', hz(TEAL) + AC)}</div>'''
group = ''
for item in CARDS:
    if len(item) == 3:
        if group:
            sections += group + '</div>'
        group = (f'<div class="fam" data-shot><h2><span class="famkey">{item[0]}</span>{item[1]}'
                 f' <small>{"— " + item[2] if item[2] else ""}</small></h2>')
    else:
        group += card(*item[:4], *item[4:])
sections += group + '</div>'

HTML = f'''<title>Refining the chosen logo — 25 to 36</title>
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
.harmony .light .dom,.harmony .light .tag{{color:{TEAL_D}}}
.bar{{height:64px;background:#0b2033;display:flex;align-items:center;gap:20px;padding:0 18px;overflow:hidden}}
.barlab{{font:600 12px system-ui;color:#7fa3bd;flex:none}}
.bar .wm{{color:#fff}} .bar .tag,.bar .dom{{color:#b3d1e7}}
</style>
<div class="wrap">
<h1>Refining the chosen logo</h1>
<p class="lede">Option <b>24</b> is live; every card below changes <b>one thing</b> about it — how the horizon line is drawn, its shade, the aircraft's attitude, the type — and <b>36</b> combines the strongest of them. Same drill: dark, light, and the real 64px header. Say the number.</p>
{sections}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/refine.html')
out.write_text(HTML)
print(f'wrote {out}, {len(HTML)//1024} KB')
