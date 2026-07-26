/**
 * Cycle-15 verification: confirm the two conversion events actually reach GA4.
 *
 * The page defines its own `function gtag(){ dataLayer.push(arguments) }`, so a
 * stubbed window.gtag gets overwritten — the honest place to assert is the
 * dataLayer queue itself, which is exactly what gtag.js consumes.
 *
 * Each scenario gets its own page: clicking a tel: link leaves Chromium with a
 * pending external-protocol navigation that silently swallows the next real
 * mouse click, so reusing one page across scenarios produces false failures.
 *
 * Usage: node scripts/verify_ga_events.mjs   (needs dist/ served on :4321)
 */
import { chromium } from 'playwright';

const BASE = process.env.BASE ?? 'http://localhost:4321';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const readEvents = (page) =>
  page.evaluate(() =>
    (window.dataLayer ?? [])
      .map((a) => Array.from(a))
      .filter((a) => a[0] === 'event')
      .map((a) => ({ name: a[1], params: a[2] }))
  );

const results = [];
const check = (name, ok, detail = '') => {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? ` — ${detail}` : ''}`);
};

const browser = await chromium.launch({ executablePath: EXE });
const ctx = await browser.newContext();
// gtag.js itself is a third-party request we neither need nor want in a test.
await ctx.route('https://www.googletagmanager.com/**', (r) => r.abort());

const open = async (path) => {
  const page = await ctx.newPage();
  await page.goto(`${BASE}${path}`, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => Array.isArray(window.dataLayer));
  // Keep the form on-page so dataLayer survives to be read.
  await page.evaluate(() =>
    document
      .querySelectorAll('form.quote-form')
      .forEach((f) => f.addEventListener('submit', (e) => e.preventDefault()))
  );
  return page;
};

// ---- 1. phone tap fires contact_phone ----
{
  const page = await open('/');
  await page.locator('a[href^="tel:"]').first().click();
  const events = await readEvents(page);
  check(
    'phone tap -> contact_phone',
    events.some((e) => e.name === 'contact_phone'),
    JSON.stringify(events)
  );
  await page.close();
}

// ---- 2. incomplete submit does NOT fire generate_lead ----
{
  const page = await open('/quote/');
  await page.evaluate(() => {
    const btn = document.querySelector('.quote-submit');
    btn.classList.remove('hidden');
    btn.click();
  });
  const events = await readEvents(page);
  check(
    'blocked submit -> no generate_lead',
    !events.some((e) => e.name === 'generate_lead'),
    JSON.stringify(events)
  );
  await page.close();
}

// ---- 3. complete submit fires generate_lead ----
{
  const page = await open('/quote/');
  await page.fill('input[name="FlyFrom"]', 'Thunder Bay');
  await page.fill('input[name="FlyTo"]', 'Pickle Lake');
  await page.fill('input[name="Passengers"]', '4');
  await page.click('.quote-next');
  await page.waitForSelector('.quote-step[data-step="2"]:not(.hidden)');
  await page.click('.quote-next');
  await page.waitForSelector('.quote-step[data-step="3"]:not(.hidden)');
  await page.fill('input[name="Name"]', 'Test Person');
  await page.fill('input[name="Email"]', 'test@example.com');
  await page.click('.quote-submit');
  const events = await readEvents(page);
  const lead = events.find((e) => e.name === 'generate_lead');
  check('complete submit -> generate_lead', !!lead, JSON.stringify(events));
  check(
    'generate_lead carries source_page + subject',
    !!lead?.params?.source_page && lead?.params?.form_subject !== undefined,
    lead ? JSON.stringify(lead.params) : 'no event'
  );
  await page.close();
}

await browser.close();

const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
process.exit(failed.length ? 1 : 0);
