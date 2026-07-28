import { chromium } from '/home/user/Charterflightnetwork/node_modules/playwright/index.mjs';
const BASE = process.env.BASE ?? 'http://localhost:4321';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const results = [];
const check = (n, ok, d = '') => { results.push(ok); console.log(`${ok ? 'PASS' : 'FAIL'}  ${n}${d ? ' — ' + d : ''}`); };

// JS path
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
await page.goto('http://localhost:4321/directory/', { waitUntil: 'networkidle' });
check('finder visible with JS', await page.locator('.operator-finder').isVisible());
await page.fill('.finder-q', 'kenora');
await page.waitForTimeout(400);
const kenoraCount = await page.locator('.finder-results li').count();
const countText = await page.locator('.finder-count').textContent();
check('search "kenora" returns results', kenoraCount > 0, `${kenoraCount} cards, "${countText.trim()}"`);
await page.fill('.finder-q', '');
await page.selectOption('.finder-prov', 'Manitoba');
await page.click('.finder-chip[data-service="Floats"]');
await page.waitForTimeout(300);
const mbText = await page.locator('.finder-count').textContent();
const firstCard = await page.locator('.finder-results li').first().textContent();
check('Manitoba + Floats filter works', /\d+ operators? match/.test(mbText) && !mbText.startsWith('0 '), mbText.trim());
check('card has phone or directory link', /Directory page/.test(firstCard));
// phones exist only where the source directory pages list them (223/530);
// the default featured-first view has plenty — assert there.
await page.selectOption('.finder-prov', '');
await page.click('.finder-chip[data-service="Floats"]'); // toggle Floats back off
await page.waitForTimeout(300);
const telCount = await page.locator('.finder-results a[href^="tel:"]').count();
check('tel: links render (GA delegated listener covers them)', telCount > 0, `${telCount} phone links in default view`);
// visual reference goes to the OS temp dir, never the repo working tree
await page.screenshot({
  path: (process.env.TMPDIR ?? '/tmp') + '/finder-verify.png',
  clip: { x: 0, y: 260, width: 1280, height: 620 },
});
await page.close();

// deep-link path: province hubs link to /directory/?prov=...#find-an-operator
{
  const page = await browser.newPage();
  await page.goto(`${BASE}/directory/?prov=British%20Columbia&type=Helicopter`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  const c = (await page.locator('.finder-count').textContent()).trim();
  const chipOn = await page.locator('.finder-chip[data-service="Helicopter"]').getAttribute('aria-pressed');
  const provVal = await page.locator('.finder-prov').inputValue();
  check(
    'URL params pre-filter the finder (prov + type)',
    provVal === 'British Columbia' && chipOn === 'true' && /^[1-9]\d* operators? match/.test(c),
    c
  );
  await page.close();
}

// no-JS path
const nojs = await browser.newPage({ javaScriptEnabled: false });
await nojs.goto('http://localhost:4321/directory/', { waitUntil: 'domcontentloaded' });
check('no-JS: finder hidden, province lists intact', !(await nojs.locator('.operator-finder').isVisible()) && (await nojs.locator('h2:has-text("Ontario")').isVisible()));
await nojs.close();
await browser.close();
console.log(`\n${results.filter(Boolean).length}/${results.length} checks passed`);
process.exit(results.every(Boolean) ? 0 : 1);
