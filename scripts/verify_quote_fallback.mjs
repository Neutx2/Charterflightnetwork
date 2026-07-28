/**
 * Verify the /quote multi-step pre-paint collapse and its self-healing
 * fallback (BACKLOG 5b).
 *
 * The inline js-ms script hides steps 2-3 before first paint so the deferred
 * enhancement causes no layout shift. That is only safe if the failure path
 * holds: when the enhancement module never runs, the watchdog must restore
 * the full single-page form — otherwise the contact fields are trapped
 * hidden and the page cannot convert at all.
 *
 * Usage: node scripts/verify_quote_fallback.mjs   (needs dist/ served on :4321)
 */
import { chromium } from 'playwright';

const BASE = process.env.BASE ?? 'http://localhost:4321';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const results = [];
const check = (name, ok, detail = '') => {
  results.push(ok);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? ` — ${detail}` : ''}`);
};

const browser = await chromium.launch({ executablePath: EXE });

// ---------- 1. normal path: multi-step active, no shift-prone state ----------
{
  const page = await browser.newPage();
  await page.goto(`${BASE}/quote/`, { waitUntil: 'networkidle' });
  const state = await page.evaluate(() => {
    const form = document.querySelector('form.quote-form');
    const vis = (sel) => {
      const el = form.querySelector(sel);
      return el && getComputedStyle(el).display !== 'none';
    };
    return {
      ready: form.dataset.msReady === '1',
      jsMs: form.classList.contains('js-ms'),
      step1: vis('[data-step="1"]'),
      step3: vis('[data-step="3"]'),
      progress: vis('.quote-progress'),
      next: vis('.quote-next'),
      submit: vis('.quote-submit'),
    };
  });
  check('enhancement takes over (data-ms-ready, js-ms dropped)', state.ready && !state.jsMs);
  check('step 1 visible, step 3 hidden, progress + Continue shown', state.step1 && !state.step3 && state.progress && state.next && !state.submit);
  await page.close();
}

// ---------- 2. failure path: module never runs -> watchdog restores full form ----------
// Astro inlines the enhancement module into the HTML, so "module blocked" in
// production means CSP, a runtime error, or the connection stalling after the
// form markup but before the end-of-body module arrives. Simulate by serving
// the page with every module script stripped; the classic inline js-ms
// script (no type attribute) still runs.
{
  const page = await browser.newPage({ javaScriptEnabled: true });
  await page.route('**/quote/', async (route) => {
    const res = await route.fetch();
    const html = (await res.text()).replace(/<script type="module">[\s\S]*?<\/script>/g, '');
    await route.fulfill({ response: res, body: html });
  });
  await page.goto(`${BASE}/quote/`, { waitUntil: 'domcontentloaded' });
  const before = await page.evaluate(() => {
    const form = document.querySelector('form.quote-form');
    const el = form.querySelector('[data-step="3"]');
    return { jsMs: form.classList.contains('js-ms'), step3: getComputedStyle(el).display !== 'none' };
  });
  check('with module blocked, pre-paint state engages first', before.jsMs && !before.step3);
  await page.waitForFunction(
    () => !document.querySelector('form.quote-form').classList.contains('js-ms'),
    { timeout: 6000 }
  );
  const after = await page.evaluate(() => {
    const form = document.querySelector('form.quote-form');
    const vis = (sel) => getComputedStyle(form.querySelector(sel)).display !== 'none';
    return { step1: vis('[data-step="1"]'), step2: vis('[data-step="2"]'), step3: vis('[data-step="3"]'), submit: vis('.quote-submit'), progress: vis('.quote-progress') };
  });
  check(
    'watchdog restores full single-page form (all steps + submit, no progress)',
    after.step1 && after.step2 && after.step3 && after.submit && !after.progress
  );
  await page.close();
}

// ---------- 3. no-JS path unchanged ----------
{
  const page = await browser.newPage({ javaScriptEnabled: false });
  await page.goto(`${BASE}/quote/`, { waitUntil: 'domcontentloaded' });
  const state = await page.evaluate ? await page.evaluate(() => true).catch(() => null) : null;
  // JS disabled: evaluate is unavailable-ish in some drivers; use locators.
  const step3 = await page.locator('form.quote-form [data-step="3"]').isVisible();
  const submit = await page.locator('form.quote-form .quote-submit').isVisible();
  const progress = await page.locator('form.quote-form .quote-progress').isVisible();
  check('no-JS renders the full single-page form', step3 && submit && !progress, String(state ?? ''));
  await page.close();
}

await browser.close();
const passed = results.filter(Boolean).length;
console.log(`\n${passed}/${results.length} checks passed`);
process.exit(passed === results.length ? 0 : 1);
