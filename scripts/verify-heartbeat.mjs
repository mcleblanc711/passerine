// Run against an isolated Vite dev server. Every API response is synthetic.
import { chromium } from '../frontend/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const browser = await chromium.launch({ executablePath: process.env.PASSERINE_CHROMIUM || undefined, headless: true });
try {
  const page = await browser.newPage();
  await page.route('**/api/**', async route => {
    const path = new URL(route.request().url()).pathname;
    const observation = {
      origin: 'real', source_observed_at: null, heartbeat_at: '2026-09-18T10:00:00+00:00',
      heartbeat_note: 'Recorded MiniBench tournament heartbeat; emitted at poll start, progress and completion. It does not prove the process is still running or that work succeeded. Resolution ingestion and scoring success remain unknown.',
      job_success_at: null, coverage: 'Synthetic browser fixture', provenance: 'Fixture', data: { records: [] },
    };
    const data = path.endsWith('/session') ? { csrf: 'fixture-only' } : {
      sources: [{ id: 'whiskeyjack', connection: 'connected', collected_at: '2026-09-19T12:00:00Z', attempt_at: '2026-09-19T12:00:00Z', error: null, cache_stale: false, observation }],
      events: [], incidents: [], outbox: [], worker: { alive: true, heartbeat: '2026-09-19T12:00:00Z' },
    };
    await route.fulfill({ json: data });
  });
  for (const width of [360, 390, 430, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('http://127.0.0.1:5174/#whiskeyjack');
    await page.getByText('Recorded tournament heartbeat', { exact: false }).waitFor();
    await page.getByText('Successful job Unknown', { exact: true }).waitFor();
    assert.match(await page.locator('.evidence').innerText(), /Resolution ingestion and scoring success remain unknown/);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    if (width === 390) {
      await page.locator('.evidence').scrollIntoViewIfNeeded();
      await mkdir('runtime/screenshots', { recursive: true });
      await page.screenshot({ path: 'runtime/screenshots/heartbeat-mobile.png' });
    }
  }
  console.log('Heartbeat labels, unknown job success and no overflow verified at 360/390/430/1440px using intercepted synthetic API responses.');
} finally {
  await browser.close();
}
