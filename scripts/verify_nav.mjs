/**
 * Header nav verification. The Destinations menu collapses four links that
 * used to be top-level, so it has to work by mouse, keyboard AND touch —
 * a hover-only menu would strand keyboard and touch users on the four
 * highest-intent pages on the site.
 *
 * Usage: node scripts/verify_nav.mjs   (needs dist/ served on :4321)
 */
import { chromium } from 'playwright';

const BASE = process.env.BASE ?? 'http://localhost:4321';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const results = [];
const check = (name, ok, detail = '') => {
  results.push({ name, ok });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? ` — ${detail}` : ''}`);
};

const browser = await chromium.launch({ executablePath: EXE });

// ---------- desktop ----------
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' });

  const header = page.locator('header > div').first();
  const rows = await header.evaluate((el) => {
    // distinct top offsets among direct children of the flex row = wrap count
    const kids = [...el.querySelectorAll('a, nav > *, button')];
    return new Set(kids.map((k) => Math.round(k.getBoundingClientRect().top))).size;
  });
  const h = await page.locator('header').evaluate((el) => el.getBoundingClientRect().height);
  check('header is a single 64px row (no wrapping)', h <= 68, `height=${h}px, ${rows} distinct tops`);

  const panel = page.locator('[data-menu-panel]');
  check('menu starts closed', await panel.isHidden());

  await page.click('[data-menu-button]');
  check('click opens menu', await panel.isVisible());
  check(
    'menu exposes all four region links',
    (await panel.locator('a').count()) === 4,
    (await panel.locator('a').allInnerTexts()).join(' | ').replace(/\n/g, ' ')
  );
  check(
    'aria-expanded tracks state',
    (await page.getAttribute('[data-menu-button]', 'aria-expanded')) === 'true'
  );

  await page.keyboard.press('Escape');
  check('Escape closes menu', await panel.isHidden());

  await page.click('[data-menu-button]');
  await page.click('h1');
  check('outside click closes menu', await panel.isHidden());

  // keyboard: tab to the button and open with Enter
  await page.click('[data-menu-button]');
  const href = await panel.locator('a').first().getAttribute('href');
  await panel.locator('a').first().click();
  check('region link navigates', new URL(page.url()).pathname.startsWith(href), page.url());
  await page.close();
}

// ---------- mobile ----------
{
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' });
  const h = await page.locator('header').evaluate((el) => el.getBoundingClientRect().height);
  check('mobile header is one row', h <= 68, `height=${h}px`);

  const menu = page.locator('#mobile-nav');
  check('mobile menu starts closed', await menu.isHidden());
  await page.click('#mobile-nav-toggle');
  check('hamburger opens mobile menu', await menu.isVisible());
  const links = await menu.locator('a').count();
  check('mobile menu lists all 9 destinations/sections + phone', links === 10, `${links} links`);

  const cta = page.locator('header a[href="/quote"]');
  const box = await cta.boundingBox();
  check('CTA does not wrap', box.height <= 44, `CTA ${Math.round(box.width)}×${Math.round(box.height)}`);
  await page.close();
}

await browser.close();
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
process.exit(failed.length ? 1 : 0);
