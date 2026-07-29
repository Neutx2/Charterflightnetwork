#!/usr/bin/env node
/** Screenshot the built home page for the owner status board. */
import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';
import { spawn } from 'node:child_process';

const out = process.argv[2];
const server = spawn('python3', ['-m', 'http.server', '4399'], { cwd: 'dist', stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 1200));
try {
  const b = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  });
  const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
  await p.goto('http://localhost:4399/', { waitUntil: 'networkidle' });
  writeFileSync(out, await p.screenshot({ type: 'jpeg', quality: 76 }));
  await b.close();
} finally {
  server.kill();
}
console.log('thumb written');
