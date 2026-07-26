#!/usr/bin/env node
/**
 * Render the social share card (public/images/og-default.jpg) at 1200x630.
 *
 * Social platforms don't render SVG, so the brand mark + wordmark are drawn in
 * HTML and rasterised with the bundled Chromium. Re-run after any logo change:
 *   node scripts/build_og_image.mjs
 */
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const outDir = join(ROOT, 'public', 'images');
mkdirSync(outDir, { recursive: true });

const outfit = readFileSync(join(ROOT, 'public/fonts/outfit-latin-wght-normal.woff2')).toString('base64');
const inter = readFileSync(join(ROOT, 'public/fonts/inter-latin-wght-normal.woff2')).toString('base64');

const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:"Outfit V";font-weight:100 900;src:url(data:font/woff2;base64,${outfit}) format("woff2-variations")}
@font-face{font-family:"Inter V";font-weight:100 900;src:url(data:font/woff2;base64,${inter}) format("woff2-variations")}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;position:relative;
  background:linear-gradient(150deg,#12314a 0%,#0b2033 58%,#0d2a22 100%);
  color:#f2f6fa;font-family:"Inter V",sans-serif;display:flex;flex-direction:column;
  justify-content:center;padding:76px 84px}
/* boreal horizon + arc echo, kept faint so the type owns the card */
.ridge{position:absolute;left:0;right:0;bottom:0;height:230px;
  background:linear-gradient(180deg,transparent,rgba(13,31,26,.85));}
svg.trees{position:absolute;left:0;bottom:0;width:1200px;height:210px;opacity:.7}
.arc{position:absolute;right:-60px;top:-120px;width:620px;height:620px;
  border-radius:50%;border:3px solid rgba(232,148,15,.16)}
.brand{display:flex;align-items:center;gap:20px;margin-bottom:34px;position:relative}
.brand svg{filter:drop-shadow(0 6px 14px rgba(0,0,0,.35))}
.brand b{font-family:"Outfit V",sans-serif;font-weight:700;font-size:32px;letter-spacing:-.01em}
h1{position:relative;font-family:"Outfit V",sans-serif;font-weight:700;font-size:70px;
  line-height:1.06;letter-spacing:-.02em;max-width:16ch}
h1 em{font-style:normal;color:#f5a623}
p{position:relative;margin-top:26px;font-size:26px;color:#bed3e4;max-width:34ch;line-height:1.4}
.strip{position:relative;margin-top:40px;display:flex;gap:34px;font-size:20px;
  font-weight:600;color:#9fc4b5}
.strip span::before{content:"✓ ";color:#5e9f85}
</style>
<div class="arc"></div>
<svg class="trees" viewBox="0 0 1200 210" preserveAspectRatio="none"><g fill="#0d1f1a">
${Array.from({ length: 60 }, (_, i) => {
  const x = i * 20 + (i % 3) * 4;
  const h = 96 + ((i * 37) % 62);
  return `<path d="M${x} 210 l${11 + (i % 4)} -${h} l${11 + (i % 4)} ${h} Z"/>`;
}).join('')}
</g></svg>
<div class="ridge"></div>

<div class="brand">
  <svg width="64" height="64" viewBox="0 0 64 64">
    <rect width="64" height="64" rx="15" fill="#1d486b"/>
    <g fill="#faf8f4"><path d="M32 7.4c2.8 0 4.7 2.2 4.7 4.9l-1.7 14.6c-.2 1.8-1.3 2.8-3 2.8s-2.8-1-3-2.8L27.3 12.3c0-2.7 1.9-4.9 4.7-4.9z"/><path d="M55.3 47.6c-1.4 2.4-4.4 3.1-6.7 1.7l-12.4-8.1c-1.5-1-1.9-2.4-1.1-3.9s2.2-1.9 3.9-1.3l13.9 5.5c2.4 1 3.8 3.7 2.4 6.1z"/><path d="M8.7 47.6c-1.4-2.4 0-5.1 2.4-6.1l13.9-5.5c1.7-.6 3.1-.2 3.9 1.3s.4 2.9-1.1 3.9l-12.4 8.1c-2.3 1.4-5.3.7-6.7-1.7z"/></g><circle cx="32" cy="32" r="6.6" fill="#e8940f"/>
  </svg>
  <b>Charter Flight Network</b>
</div>
<h1>Charter flights across Canada — <em>up to 3 competitive quotes</em>.</h1>
<p>Jet, turboprop, float plane and helicopter charters. Free, no obligation.</p>
<div class="strip"><span>No cost</span><span>Book direct</span><span>Canadian since 2008</span></div>`;

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.setContent(html, { waitUntil: 'load' });
await page.waitForTimeout(300);
const buf = await page.screenshot({ type: 'jpeg', quality: 88 });
writeFileSync(join(outDir, 'og-default.jpg'), buf);
await browser.close();
console.log(`wrote public/images/og-default.jpg (${Math.round(buf.length / 1024)} KB)`);
