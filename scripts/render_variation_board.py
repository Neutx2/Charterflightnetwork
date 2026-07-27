#!/usr/bin/env python3
"""The full decision board: every worthwhile variation of the direction the
owner picked (aircraft behind "Network" at the measured 2/3 size, over a sun
or horizon), one variable changed at a time, numbered so choosing is saying a
number.

Geometry is the calibrated artboard from the earlier studies and is IDENTICAL
in every card unless the card's whole point is to vary it:
    cap line          y = 105
    "Network"         x 237..390, centred x = 313
    aircraft          scale 1.7 (102u = 2/3 of "Network"), centre (313, 90),
                      rotate 38 — cy = 105 - 9*scale keeps ~65% visible
    viewport clip     y = 120 (art below this never renders)
"""
import base64
import pathlib

ROOT = pathlib.Path('/home/user/Charterflightnetwork')
FONT = base64.b64encode((ROOT / 'public/fonts/outfit-latin-wght-normal.woff2').read_bytes()).decode()
LEGACY = base64.b64encode((ROOT / 'src/assets/legacy/Logo_green_white.jpg').read_bytes()).decode()

O = '#ff7d02'
TEAL = '#2d7b8c'
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 1.3'
         'l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6'
         'l16.3-9.6v-9.1C27.8 10.9 29.4 8 32 8z')
plane = lambda t, f=O: f'<g transform="{t} translate(-32 -32)" fill="{f}"><path d="{PLANE}"/></g>'

VB = '0 -60 460 180'
PLACE = 'left:-.06em;top:-2.7em;height:4.5em;width:11.5em'

# The two bases the owner picked, byte for byte from the previous study.
HZ = (f'<path d="M-16 132C90 74 370 74 476 132" stroke="{O}" stroke-width="6"'
      f' stroke-linecap="round" fill="none"/>')
SUN = f'<circle cx="118" cy="165" r="71" fill="{O}"/>'
AC = plane('translate(313 90) rotate(38) scale(1.7)')      # the favoured aircraft

def hz(w, extra=''):
    return (f'<path d="M-16 132C90 74 370 74 476 132" stroke="{O}" stroke-width="{w}"'
            f' stroke-linecap="round" {extra} fill="none"/>')

# (number, name, note, art) — sections mark where a family starts
CARDS = [
    ('A', 'Horizon family', 'the wide horizon you liked, with its line varied'),
    ('1', 'Wide horizon', 'exactly as shown before — the favourite, unchanged', HZ + AC),
    ('2', 'Fine horizon', 'a thinner, more elegant line', hz(4) + AC),
    ('3', 'Bold horizon', 'a heavier line with more presence', hz(8.5) + AC),
    ('4', 'Dashed horizon', 'the line drawn as a contrail', hz(5, 'stroke-dasharray="2 8"') + AC),
    ('5', 'Double horizon', 'a solid line with a dashed echo — nearest the classic twin swoosh',
     hz(6) + f'<path d="M6 143C104 87 356 87 454 143" stroke="{O}" stroke-width="3.6"'
     f' stroke-linecap="round" stroke-dasharray="2 7" fill="none"/>' + AC),

    ('B', 'Sun family', 'the small sun you liked, with the disc varied'),
    ('6', 'Small sun', 'exactly as shown before — the favourite, unchanged', SUN + AC),
    ('7', 'Broad sun', 'a wider, lower dome across the first word',
     f'<circle cx="118" cy="214" r="120" fill="{O}"/>' + AC),
    ('8', 'Sunburst', 'the small sun with short rays breaking above the letters',
     SUN + f'<g stroke="{O}" stroke-width="4" stroke-linecap="round">'
     f'<path d="M118 82v-12"/><path d="M83 88l-6-11"/><path d="M153 88l6-11"/>'
     f'<path d="M52 102l-10-8"/><path d="M184 102l10-8"/></g>' + AC),
    ('9', 'Sun under the aircraft', 'the disc moved beneath the aircraft — it climbs straight out of the sun',
     f'<circle cx="313" cy="165" r="71" fill="{O}"/>'
     + plane('translate(320 36) rotate(38) scale(1.7)')),
    ('10', 'Sunrise on the horizon', 'sun and horizon together — the full scene',
     HZ + SUN + AC),

    ('C', 'Aircraft variations', 'on the wide horizon — only the aircraft changes'),
    ('11', 'Steeper climb', 'pitched up harder — more energy',
     HZ + plane('translate(313 90) rotate(50) scale(1.7)')),
    ('12', 'Gentler climb', 'a shallower, calmer angle',
     HZ + plane('translate(313 92) rotate(28) scale(1.7)')),
    ('13', 'Flying clear', 'the aircraft fully above the letters, nothing hidden',
     HZ + plane('translate(313 54) rotate(38) scale(1.7)')),
    ('14', 'Climbing off the end', 'moved to the right, leaving past the end of the word',
     HZ + plane('translate(368 84) rotate(38) scale(1.7)')),

    ('D', 'A quieter colour', 'one alternative for the line itself'),
    ('15', 'Teal horizon', 'the horizon in the site\'s deep teal, only the aircraft orange',
     f'<path d="M-16 132C90 74 370 74 476 132" stroke="{TEAL}" stroke-width="6"'
     f' stroke-linecap="round" fill="none"/>' + AC),

    ('E', 'Journeys', 'the logo tells the story of a flight'),
    # Route: origin dot, dashed great-circle that passes behind the word and
    # emerges rising into the aircraft. End tangent (25,-32) matches the
    # aircraft's 38-degree heading, so the route and the aircraft agree.
    ('16', 'Route to anywhere', 'a departure point, a dashed route behind the word, the aircraft flying it',
     f'<circle cx="24" cy="96" r="5.5" fill="{O}"/>'
     f'<path d="M24 96C110 10 267 126 292 94" stroke="{O}" stroke-width="4.5"'
     f' stroke-linecap="round" stroke-dasharray="2 8" fill="none"/>'
     + plane('translate(320 58) rotate(38) scale(1.55)')),
    ('17', 'Take-off run', 'a runway of long dashes along the letter tops, the aircraft rotating off the end',
     f'<path d="M8 100H224" stroke="{O}" stroke-width="6" stroke-dasharray="16 11" fill="none"/>'
     + plane('translate(298 66) rotate(38) scale(1.55)')),
    ('18', 'The fleet', 'three aircraft in formation — the network itself, flying together',
     HZ + plane('translate(340 46) rotate(38) scale(1.35)')
     + plane('translate(268 82) rotate(38) scale(.9)')
     + plane('translate(222 106) rotate(38) scale(.65)')),
    # Underline needs a deeper artboard: same 0.025em/unit mapping, viewport
    # extended to y=180 so a line under the baseline isn't clipped.
    # End tangent P3-P2 = (102,-28) -> heading atan2(102,28) = 74.6deg, and the
    # aircraft sits on that tangent extended, past the end of ".com".
    ('19', 'Underline sweep', 'the line runs under the whole name and lifts into the aircraft past .com',
     f'<path d="M10 146C130 170 340 168 442 140" stroke="{O}" stroke-width="6"'
     f' stroke-linecap="round" fill="none"/>'
     + plane('translate(479 130) rotate(75) scale(1.05)'),
     '0 -60 512 240', 'left:-.06em;top:-2.7em;height:6em;width:12.8em'),

    ('F', 'Emblems & Canada', 'a mark rising behind the word'),
    ('20', 'Compass ring', 'an open ring rising behind “Network”, the aircraft flying within it',
     f'<circle cx="313" cy="62" r="55" stroke="{O}" stroke-width="6.5" fill="none"/>'
     f'<g stroke="{O}" stroke-width="5" stroke-linecap="round">'
     f'<path d="M313 3v-11"/><path d="M254 62h-11"/><path d="M372 62h11"/></g>'
     + plane('translate(313 58) rotate(38) scale(1.15)')),
    ('21', 'Around the globe', 'a small globe rising behind “Network”, the aircraft climbing away',
     f'<circle cx="313" cy="80" r="44" stroke="{O}" stroke-width="6" fill="none"/>'
     f'<path d="M271 88Q313 102 355 88" stroke="{O}" stroke-width="4" fill="none"/>'
     f'<path d="M276 62Q313 74 350 62" stroke="{O}" stroke-width="4" fill="none"/>'
     + plane('translate(382 26) rotate(38) scale(1.3)')),
    ('22', 'The big sunrise', 'one broad dome behind the whole name, the aircraft well clear',
     f'<circle cx="230" cy="250" r="165" fill="{O}"/>'
     + plane('translate(338 38) rotate(38) scale(1.7)')),
    # The leaf is a union of five narrow pointed lobes about a common centre
    # plus a stem — a plotted-point outline rendered as a starburst, this
    # doesn't. Deep notches between lobes are what make it read as maple.
    ('23', 'Maple climb', 'the maple leaf where the sun was — Canadian owned, said quietly',
     f'<g transform="translate(112 64) scale(1.15)" fill="{O}">'
     f'<path d="M0 -28L7 -8L0 0L-7 -8Z"/>'
     f'<path transform="rotate(52)" d="M0 -23L6 -7L0 0L-6 -7Z"/>'
     f'<path transform="rotate(-52)" d="M0 -23L6 -7L0 0L-6 -7Z"/>'
     f'<path transform="rotate(90)" d="M0 -18L5 -6L0 0L-5 -6Z"/>'
     f'<path transform="rotate(-90)" d="M0 -18L5 -6L0 0L-5 -6Z"/>'
     f'<rect x="-1.6" y="-2" width="3.2" height="16"/></g>' + AC),
]


def lockup(art, px, tag, vb=VB, place=PLACE, padtop='1.6em'):
    tg = '<span class="tag">Canadian owned &amp; operated since 2008</span>' if tag else ''
    return (f'<span class="lk" style="font-size:{px}px;padding-top:{padtop}">'
            f'<svg style="position:absolute;pointer-events:none;{place}" viewBox="{vb}"'
            f' preserveAspectRatio="xMinYMid meet">{art}</svg>'
            f'<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>'
            f'{tg}</span>')


# The current live logotype, reproduced from src/lib/wordmark-arcs.ts verbatim.
CLASSIC = (
    f'<path d="M4 42C32 6 96 2 136 24" stroke="{O}" stroke-width="7.5" stroke-linecap="round" fill="none"/>'
    f'<path d="M16 46C42 18 96 14 132 32" stroke="{O}" stroke-width="4.5" stroke-linecap="round"'
    f' stroke-dasharray="2 7" fill="none"/>'
    + plane('translate(152 6) rotate(34) scale(.86)'))
CL_VB = '0 0 200 56'
CL_PLACE = 'left:.02em;top:-.42em;height:1.7em;width:4.6em'


def card(num, name, note, art, vb=VB, place=PLACE, padtop='1.6em'):
    lk = lambda px, tag: lockup(art, px, tag, vb, place, padtop)
    return f'''<section class="card" data-shot>
  <header><span class="num">{num}</span><b>{name}</b><span class="ds">{note}</span></header>
  <div class="panes"><div class="pane dark">{lk(17, True)}{lk(34, False)}</div>
  <div class="pane light">{lk(17, True)}{lk(26, False)}</div></div>
  <div class="bar"><span class="barlab">on the real website header</span>{lk(17, True)}</div></section>'''


REFS = f'''<div class="refs" data-shot>
<section class="card ref"><header><span class="num gray">then</span><b>The original — 2008</b>
<span class="ds">the logo the site has carried since the beginning</span></header>
<div class="pane light refpane"><img src="data:image/jpeg;base64,{LEGACY}" alt="" style="max-width:520px;width:100%"></div></section>
<section class="card ref"><header><span class="num gray">now</span><b>Currently on the new site</b>
<span class="ds">the classic climb — swoosh and contrail ahead of the word</span></header>
<div class="panes"><div class="pane dark">{lockup(CLASSIC, 17, True, CL_VB, CL_PLACE, '.72em')}{lockup(CLASSIC, 34, False, CL_VB, CL_PLACE, '.72em')}</div>
<div class="pane light">{lockup(CLASSIC, 17, True, CL_VB, CL_PLACE, '.72em')}{lockup(CLASSIC, 26, False, CL_VB, CL_PLACE, '.72em')}</div></div></section>
</div>'''

sections = REFS
group = ''
for item in CARDS:
    if len(item) == 3:
        if group:
            sections += group + '</div>'
        group = (f'<div class="fam" data-shot><h2><span class="famkey">{item[0]}</span>{item[1]}'
                 f' <small>— {item[2]}</small></h2>')
    else:
        n, name, note, art, *extra = item
        group += card(n, name, note, art, *extra)
if group:
    sections += group + '</div>'

HTML = f'''<title>Charter Flight Network — logo variations</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:30px 20px 60px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 30px Outfit;letter-spacing:-.6px;margin:0 0 8px}}
h2{{font:800 21px Outfit;margin:0 0 14px;display:flex;align-items:center;gap:10px}}
h2 small{{font:400 15px system-ui;color:#8fb0c8}}
.famkey{{background:#ffffff14;border:1px solid #ffffff2a;color:#ffb36b;font:800 14px Outfit;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;flex:none}}
.lede{{color:#9db9cf;font:400 16px system-ui;margin:0 0 26px;max-width:76ch;line-height:1.6}}
.fam{{margin-top:36px;padding-top:20px;border-top:1px solid #ffffff1a}}
.refs{{margin-bottom:8px}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:14px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:13px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 16px Outfit;min-width:34px;height:30px;padding:0 8px;border-radius:8px;display:grid;place-items:center;flex:none}}
.num.gray{{background:#3d566b;color:#dbe9f4;font-size:13px}}
.card header b{{font:700 16px Outfit}}.ds{{color:#8fb0c8;font:400 14px system-ui}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:30px 22px;display:flex;align-items:center;gap:38px;flex-wrap:wrap;min-height:150px}}
.refpane{{justify-content:center;padding:26px}}
.dark{{background:#12314a}}.light{{background:#faf8f4}}
.lk{{position:relative;display:block;flex:none;line-height:1.12}}
.wm{{position:relative;display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm em{{font-style:normal;color:{O}}}
.tag{{position:relative;display:block;font:400 11px system-ui;white-space:nowrap;margin-top:1px}}
.dark .wm{{color:#fff}}.dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}}.light .tag,.light .dom{{color:#5b7185}}.light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
.bar{{height:64px;background:#0b2033;display:flex;align-items:center;gap:20px;padding:0 18px;overflow:hidden}}
.barlab{{font:600 12px system-ui;color:#7fa3bd;flex:none}}
.bar .wm{{color:#fff}} .bar .tag,.bar .dom{{color:#b3d1e7}}
</style>
<div class="wrap">
<h1>Charter Flight Network — the logo, 23 ways</h1>
<p class="lede">Families A–D vary the chosen direction — the aircraft behind “Network” at two-thirds of the word's width — <b>one thing at a time</b>: the horizon line, the sun, the aircraft. Numbers <b>1</b> and <b>6</b> are the two favourites exactly as shown before. Families E–F go further afield: routes, runways, a formation, a compass, a globe, the maple leaf. Each option appears small and large, on dark and light, and inside the real website header. <b>To choose, just say the number.</b></p>
{sections}</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/variations.html')
out.write_text(HTML)
print(f'wrote {out} — 23 variations + 2 references, {len(HTML)//1024} KB')
