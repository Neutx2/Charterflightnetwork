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
import { readdirSync, readFileSync, writeFileSync, statSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';

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

// Preview robots.txt: disallow everything (belt-and-suspenders with the
// injected noindex meta). Production keeps the permissive robots.txt from
// public/ untouched because this script never runs for production deploys.
writeFileSync(join(dist, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
console.log('preview robots.txt set to Disallow: /');

// Legacy-URL fallbacks for the preview host: GitHub Pages cannot serve real
// 301s, so emit a meta-refresh page at every legacy .htm/.html path. These
// are SOFT client-side redirects for preview/testing only — production runs
// on a host that serves the real 301 map (redirects/.htaccess or _redirects).
const mapPath = new URL('../crawl/redirects.json', import.meta.url).pathname;
let fallbacks = 0;
if (existsSync(mapPath)) {
  const redirects = JSON.parse(readFileSync(mapPath, 'utf8'));
  for (const [oldPath, newPath] of Object.entries(redirects)) {
    if (oldPath === '/' || oldPath.replace(/\/$/, '') === newPath.replace(/\/$/, '')) continue;
    const target = `${base}${newPath === '/' ? '/' : newPath + '/'}`;
    const out = join(dist, decodeURIComponent(oldPath).replace(/^\//, ''));
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(
      out,
      `<!doctype html><html lang="en"><head><meta charset="utf-8">` +
        `<meta name="robots" content="noindex">` +
        `<meta http-equiv="refresh" content="0; url=${target}">` +
        `<link rel="canonical" href="https://charterflightnetwork.com${newPath}">` +
        `<title>Redirecting…</title></head>` +
        `<body><p>This page has moved to <a href="${target}">${target}</a>.</p></body></html>\n`
    );
    fallbacks++;
  }
}
console.log(`wrote ${fallbacks} legacy-URL meta-refresh fallback pages`);
