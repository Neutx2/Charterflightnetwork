#!/usr/bin/env python3
"""Render the round-2 logotype explorations (options 9-18) as a standalone page.

Run from the repo root:
    python3 scripts/render_logo_options.py

Round 1 (options 1-8) lives in src/lib/wordmark-arcs.ts and is wired into the
site — those vary only the swoosh, which the Wordmark component already treats
as data. Round 2 varies things the component does not yet parameterise: type
weight, word spacing, where the two-tone break falls, and whether there is a
separate mark. They are explorations, not shipped code; whichever is chosen
gets built into Wordmark.astro properly.

Round 1 varied only the swoosh. This round varies the things that actually
change a logotype's character: type weight and spacing, where the two-tone
break falls, whether the words are closed up, and whether there is a separate
mark at all.
"""
import base64, pathlib

FONT = base64.b64encode(
    pathlib.Path('public/fonts/outfit-latin-wght-normal.woff2').read_bytes()
).decode()

O = '#ff7d02'
PLANE = ('M32 8c2.6 0 4.2 2.9 4.2 7.4v9.1l16.3 9.6c.9.5 1.5 1.5 1.5 2.6v4.1c0 .9-.9 1.6-1.8 '
         '1.3l-16-5.2v9.4l4.6 3.7c.5.4.8 1 .8 1.6v2.2c0 .8-.7 1.3-1.4 1.1L32 52.8l-8.2 1.1c-.7.2-1.4-.3-1.4-1.1'
         'v-2.2c0-.6.3-1.2.8-1.6l4.6-3.7v-9.4l-16 5.2c-.9.3-1.8-.4-1.8-1.3v-4.1c0-1.1.6-2.1 1.5-2.6l16.3-9.6'
         'v-9.1C27.8 10.9 29.4 8 32 8z')


def plane(t, fill=O):
    return f'<g transform="{t} translate(-32 -32)" fill="{fill}"><path d="{PLANE}"/></g>'


# The classic swoosh, reused where a variant isn't changing it.
CLASSIC_ARC = (f'<path d="M4 42C32 6 96 2 136 24" stroke="{O}" stroke-width="7.5" stroke-linecap="round" fill="none"/>'
               f'<path d="M16 46C42 18 96 14 132 32" stroke="{O}" stroke-width="4.5" stroke-linecap="round" '
               f'stroke-dasharray="2 7" fill="none"/>' + plane('translate(152 6) rotate(34) scale(.86)'))

# word() builds the type line; each variant supplies its own.
CLOSED = ('<span class="wm">Charterflight<em>Network</em><span class="dom">.com</span></span>')

VARIANTS = [
    dict(n=9, key='light-flight', label='Weight contrast',
         note='“Charter” heavy, “flight” light — the word breathes',
         arc=dict(place='left:.02em;top:-.42em;height:1.7em;width:4.6em', vb='0 0 200 56', paths=CLASSIC_ARC),
         word='<span class="wm">Charter<span class="lt">flight</span><em>Network</em>'
              '<span class="dom">.com</span></span>'),

    dict(n=10, key='spaced', label='Three words',
         note='spaces restored — reads as the company name, not a domain',
         arc=dict(place='left:.02em;top:-.42em;height:1.7em;width:4.4em', vb='0 0 200 56', paths=CLASSIC_ARC),
         word='<span class="wm">Charter Flight <em>Network</em></span>'),

    dict(n=11, key='mono-white', label='One colour',
         note='all-white type, the swoosh carries the orange alone',
         arc=dict(place='left:.02em;top:-.42em;height:1.7em;width:4.6em', vb='0 0 200 56', paths=CLASSIC_ARC),
         word='<span class="wm">CharterflightNetwork<span class="dom">.com</span></span>'),

    dict(n=12, key='inverted', label='Inverted split',
         note='orange first, white second — echoes the gold/red legacy version',
         arc=dict(place='left:.02em;top:-.42em;height:1.7em;width:4.6em', vb='0 0 200 56', paths=CLASSIC_ARC),
         word='<span class="wm"><em>Charterflight</em>Network<span class="dom">.com</span></span>'),

    dict(n=13, key='rule', label='Rule and lift-off',
         note='a rule underscores the word and the aircraft leaves it',
         arc=dict(place='left:0;top:.92em;height:1.15em;width:12.6em', vb='0 0 500 48',
                  paths=f'<path d="M4 34h394" stroke="{O}" stroke-width="7" stroke-linecap="round" fill="none"/>'
                        + plane('translate(432 22) rotate(-34) scale(.78)')),
         word=CLOSED, under=True),

    dict(n=14, key='from-the-c', label='Out of the C',
         note='the swoosh grows from inside the C rather than floating above',
         arc=dict(place='left:.08em;top:.06em;height:1.32em;width:4.1em', vb='0 0 200 66',
                  paths=f'<path d="M10 52C10 22 74 6 128 24" stroke="{O}" stroke-width="7.6" '
                        f'stroke-linecap="round" fill="none"/>'
                        + plane('translate(148 12) rotate(36) scale(.84)')),
         word=CLOSED),

    dict(n=15, key='stacked', label='Stacked',
         note='two decks — the most compact, best where width is short',
         arc=dict(place='left:.02em;top:-.34em;height:1.4em;width:3.9em', vb='0 0 200 56', paths=CLASSIC_ARC),
         word='<span class="wm" style="line-height:.98">Charterflight<br>'
              '<em style="letter-spacing:.14em;font-size:.74em">NETWORK</em>'
              '<span class="dom" style="letter-spacing:.05em">.com</span></span>'),

    dict(n=16, key='roundel', label='Roundel',
         note='a separate badge beside the word — works alone as an app icon',
         mark=f'<svg class="badge" viewBox="0 0 64 64"><circle cx="32" cy="32" r="31" fill="#1c5b6a"/>'
              f'<path d="M8 42C14 20 38 12 50 24" stroke="{O}" stroke-width="5.4" stroke-linecap="round" fill="none"/>'
              + plane('translate(50 17) rotate(36) scale(.62)') + '</svg>',
         word=CLOSED),

    dict(n=17, key='dotted', label='Dotted trail',
         note='no solid line at all — the whole arc is the contrail',
         arc=dict(place='left:.02em;top:-.42em;height:1.7em;width:4.6em', vb='0 0 200 56',
                  paths=f'<path d="M6 44C34 8 98 4 138 26" stroke="{O}" stroke-width="7" stroke-linecap="round" '
                        f'stroke-dasharray="1 11" fill="none"/>'
                        + plane('translate(154 8) rotate(34) scale(.86)')),
         word=CLOSED),

    dict(n=18, key='corridor', label='Twin corridor',
         note='two parallel swooshes — a route, not a single line',
         arc=dict(place='left:.02em;top:-.46em;height:1.8em;width:4.7em', vb='0 0 200 56',
                  paths=f'<path d="M4 40C32 4 96 0 134 22" stroke="{O}" stroke-width="5.4" stroke-linecap="round" fill="none"/>'
                        f'<path d="M8 52C36 20 98 14 134 34" stroke="{O}" stroke-width="5.4" stroke-linecap="round" '
                        f'opacity=".45" fill="none"/>'
                        + plane('translate(152 6) rotate(34) scale(.86)')),
         word=CLOSED),
]


def lockup(v, px, tag):
    under = v.get('under')
    pad = ('padding-bottom:1.5em' if not tag else '') if under else (
        'padding-top:.72em' if 'arc' in v else '')
    mt = '1.5em' if under else '1px'
    art = ''
    if 'arc' in v:
        a = v['arc']
        art = (f'<svg style="position:absolute;pointer-events:none;{a["place"]}" viewBox="{a["vb"]}" '
               f'preserveAspectRatio="xMinYMid meet">{a["paths"]}</svg>')
    tg = (f'<span class="tag" style="margin-top:{mt}">Canadian owned &amp; operated since 2008</span>'
          if tag else '')
    inner = f'<span class="lk" style="font-size:{px}px;{pad}">{art}{v["word"]}{tg}</span>'
    if 'mark' in v:
        return (f'<span class="row" style="font-size:{px}px">{v["mark"]}'
                f'<span class="lk">{v["word"]}{tg}</span></span>')
    return inner


cards = []
for v in VARIANTS:
    cards.append(f'''<section class="card">
  <header><span class="num">{v["n"]}</span><b>{v["label"]}</b><span class="ds">{v["note"]}</span>
  <code>{v["key"]}</code></header>
  <div class="panes">
    <div class="pane dark">{lockup(v,17,True)}{lockup(v,32,False)}</div>
    <div class="pane light">{lockup(v,17,True)}{lockup(v,26,False)}</div>
  </div>
</section>''')

html = f'''<title>CharterflightNetwork — logo options, round 2</title>
<style>
@font-face{{font-family:Outfit;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:100 900;font-display:block}}
*{{box-sizing:border-box}}
body{{background:#0b1a28;color:#fff;font-family:Outfit,system-ui;margin:0;padding:28px 20px 56px;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1120px;margin:0 auto}}
h1{{font:800 26px Outfit;letter-spacing:-.6px;margin:0 0 6px}}
.lede{{color:#8fb0c8;font:400 15px system-ui;margin:0 0 26px;max-width:64ch;line-height:1.55}}
.card{{background:#101f30;border:1px solid #ffffff16;border-radius:14px;margin-bottom:16px;overflow:hidden}}
.card header{{display:flex;align-items:center;gap:11px;flex-wrap:wrap;padding:13px 18px;border-bottom:1px solid #ffffff12}}
.num{{background:{O};color:#0b1a28;font:800 14px Outfit;width:26px;height:26px;border-radius:7px;display:grid;place-items:center;flex:none}}
.card header b{{font:700 15px Outfit;letter-spacing:-.2px}}
.ds{{color:#8fb0c8;font:400 13px system-ui}}
code{{color:#6f93ad;font:500 12px ui-monospace,monospace;background:#0b1a28;padding:3px 8px;border-radius:5px}}
.card header code{{margin-left:auto}}
.panes{{display:grid;grid-template-columns:1fr}}
@media(min-width:880px){{.panes{{grid-template-columns:1.35fr 1fr}}}}
.pane{{padding:22px;display:flex;align-items:center;gap:34px;flex-wrap:wrap;min-height:112px}}
.dark{{background:#12314a}} .light{{background:#faf8f4}}
.lk{{position:relative;line-height:1.12;display:block;flex:none}}
.row{{display:flex;align-items:center;gap:.55em;flex:none}}
.badge{{width:2.5em;height:2.5em;flex:none}}
.wm{{display:block;white-space:nowrap;font-weight:800;letter-spacing:-.035em}}
.wm .lt{{font-weight:300;letter-spacing:-.01em}}
.tag{{display:block;font:400 11px system-ui;white-space:nowrap}}
.dark .wm{{color:#fff}} .dark .tag,.dark .dom{{color:#b3d1e7}}
.light .wm{{color:#12314a}} .light .tag,.light .dom{{color:#5b7185}}
.wm em{{font-style:normal;color:{O}}} .light .wm em{{color:#e06e00}}
.dom{{font-weight:500;font-size:.62em}}
.foot{{color:#6f93ad;font:400 13px system-ui;margin-top:22px;line-height:1.7}}
</style>
<div class="wrap">
<h1>Logo options — round 2</h1>
<p class="lede">Round 1 (options 1–8) varied only the swoosh. These vary the things that actually change a logotype's character: type weight and spacing, where the two-tone break falls, whether the words are closed up, and whether there is a separate mark at all. Shown at the real header size (17px) and large, on navy and on warm white.</p>
{''.join(cards)}
<p class="foot">Numbering continues from round 1, so 1–8 and 9–18 are one set — pick any number. Round 1 is at the earlier link.</p>
</div>'''

out = pathlib.Path('/tmp/claude-0/-home-user-Charterflightnetwork/3291c930-1fc0-50cf-88b3-1ad6857d793c/scratchpad/logo-options-2.html')
out.write_text(html)
print('wrote', out, len(html) // 1024, 'KB,', len(VARIANTS), 'variants')
