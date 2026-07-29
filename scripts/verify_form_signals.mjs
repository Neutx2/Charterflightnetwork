/**
 * Non-quote form signals + confirmation variants (cycles 31/33).
 *
 * The alert signup and contact form fire their own GA4 events (sign_up,
 * contact_message) and land on adapted confirmation copy via ?from= — none
 * of which the quote-form GA suite covers. This keeps those behaviours from
 * silently regressing.
 *
 * Usage: node scripts/verify_form_signals.mjs   (needs dist/ served on :4321)
 */
import { chromium } from 'playwright';

const BASE = process.env.BASE ?? 'http://localhost:4321';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const results = [];
const check = (n, ok, d = '') => { results.push(ok); console.log(`${ok ? 'PASS' : 'FAIL'}  ${n}${d ? ' — ' + d : ''}`); };

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage();

await page.goto(`${BASE}/quote-confirmation/?from=contact`, { waitUntil: 'domcontentloaded' });
check('confirmation adapts for contact', (await page.locator('[data-confirm-heading]').textContent()).includes('Message received'));
await page.goto(`${BASE}/quote-confirmation/?from=alerts`, { waitUntil: 'domcontentloaded' });
check('confirmation adapts for alerts', (await page.locator('[data-confirm-heading]').textContent()).includes('signed up'));
await page.goto(`${BASE}/quote-confirmation/?from=operator`, { waitUntil: 'domcontentloaded' });
check('confirmation adapts for operator applications', (await page.locator('[data-confirm-heading]').textContent()).includes('Application received'));
await page.goto(`${BASE}/quote-confirmation/`, { waitUntil: 'domcontentloaded' });
check('default confirmation is the quote copy', (await page.locator('[data-confirm-heading]').textContent()).includes('forwarded to matching'));

const armCapture = () => page.evaluate(() => {
  (window).__ev = [];
  const orig = (window).gtag;
  (window).gtag = function () { (window).__ev.push([...arguments]); orig && orig.apply(this, arguments); };
  document.querySelectorAll('form').forEach((f) => f.addEventListener('submit', (e) => e.preventDefault()));
});

await page.goto(`${BASE}/empty-legs/`, { waitUntil: 'networkidle' });
await armCapture();
await page.fill('#el-name', 'T'); await page.fill('#el-email', 't@e.com');
await page.click('button:has-text("Sign Up For Alerts")');
await page.waitForTimeout(200);
const su = await page.evaluate(() => (window).__ev.filter((e) => e[1] === 'sign_up'));
check('sign_up fires on alert signup', su.length === 1 && su[0][2].method === 'empty_leg_alerts', JSON.stringify(su));

await page.goto(`${BASE}/contact/`, { waitUntil: 'networkidle' });
await armCapture();
await page.fill('#ct-name', 'T'); await page.fill('#ct-email', 't@e.com'); await page.fill('#ct-msg', 'hi');
await page.click('button:has-text("Send Message")');
await page.waitForTimeout(200);
const cm = await page.evaluate(() => (window).__ev.filter((e) => e[1] === 'contact_message'));
check('contact_message fires on contact form', cm.length === 1 && cm[0][2].source_page === '/contact/', JSON.stringify(cm));

await page.goto(`${BASE}/operators/`, { waitUntil: 'networkidle' });
await armCapture();
await page.evaluate(() => {
  document.querySelectorAll('form:not(.quote-form) input[required], form:not(.quote-form) textarea[required]').forEach((el) => {
    if (el.type === 'email') el.value = 't@e.com';
    else el.value = 'test';
  });
});
await page.click('button[type="submit"]:not(.quote-submit)');
await page.waitForTimeout(200);
const ol = await page.evaluate(() => (window).__ev.filter((e) => e[1] === 'sign_up' && e[2].method === 'operator_listing'));
check('sign_up fires on operator application', ol.length === 1, JSON.stringify(ol));

await browser.close();
const passed = results.filter(Boolean).length;
console.log(`\n${passed}/${results.length} checks passed`);
process.exit(passed === results.length ? 0 : 1);
