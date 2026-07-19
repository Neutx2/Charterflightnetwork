#!/usr/bin/env node
/**
 * Post-process dist/ for a subpath preview deployment (GitHub Pages).
 *
 *   node scripts/make-preview.mjs /Charterflightnetwork
 *
 * - rewrites root-relative href/src/action URLs in HTML to live under the base
 * - rewrites url(/...) references in CSS (self-hosted fonts)
 * - injects <meta name="robots" content="noindex"> so the preview never
 *   competes with the production domain in search
 *
 * Production deploys (real domain at /) skip this script entirely.
 */
import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const base = process.argv[2];
if (!base || !base.startsWith('/')) {
  console.error('usage: make-preview.mjs /base-path');
  process.exit(1);
}
const dist = new URL('../dist', import.meta.url).pathname;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

let htmlCount = 0;
let cssCount = 0;
for (const file of walk(dist)) {
  if (file.endsWith('.html')) {
    let html = readFileSync(file, 'utf8');
    // href="/x" src="/x" action="/x" — root-relative only (not "//" or "http...")
    html = html.replace(
      /\b(href|src|action)="\/(?!\/)/g,
      (_, attr) => `${attr}="${base}/`
    );
    html = html.replace(
      /<head>/i,
      '<head><meta name="robots" content="noindex">'
    );
    writeFileSync(file, html);
    htmlCount++;
  } else if (file.endsWith('.css')) {
    let css = readFileSync(file, 'utf8');
    const next = css.replace(/url\((['"]?)\/(?!\/)/g, (_, q) => `url(${q}${base}/`);
    if (next !== css) {
      writeFileSync(file, next);
      cssCount++;
    }
  }
}
console.log(`preview-rewrote ${htmlCount} HTML files, ${cssCount} CSS files for base ${base}`);
