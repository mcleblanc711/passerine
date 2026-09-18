// Run with .env exported; never prints passwords, session tokens or source payloads.
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';

const origin = process.env.PASSERINE_ORIGIN;
assert(origin?.startsWith('https://'), 'HTTPS origin required');
assert(process.env.PASSERINE_PASSWORD, 'Password required');
const browser = await chromium.launch({executablePath:process.env.PASSERINE_CHROMIUM || undefined});
try {
  const context = await browser.newContext({baseURL:origin, viewport:{width:390,height:844}});
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e=>errors.push(e.message));
  assert.equal((await context.request.get('/api/overview')).status(),401);
  assert.equal((await context.request.get('/api/overview', {headers:{'Tailscale-User-Login':'spoofed'}})).status(),401);
  await page.goto('/');
  await page.getByLabel('Private access password').fill(process.env.PASSERINE_PASSWORD);
  await page.getByRole('button',{name:'Open Passerine'}).click();
  await page.getByRole('heading',{name:'A view from the perch.'}).waitFor();
  const cookie=(await context.cookies()).find(c=>c.name==='passerine');
  assert(cookie?.secure && cookie.httpOnly && cookie.sameSite==='Strict');
  const session=await (await context.request.get('/api/session')).json();
  const overview=await context.request.get('/api/overview');
  assert.equal(overview.headers()['cache-control'],'no-store');
  const data=await overview.json();
  assert(data.worker.alive,'Worker heartbeat must be fresh');
  for (const id of ['wethr','whiskeyjack']) {
    const source=data.sources.find(s=>s.id===id);
    assert.equal(source.connection,'connected',`${id} read failed`);
    assert.equal(source.observation.origin,'real');
  }
  assert.equal((await context.request.post('/api/refresh',{headers:{Origin:origin}})).status(),403);
  assert.equal((await context.request.post('/api/refresh',{headers:{Origin:'https://invalid.example','x-csrf-token':session.csrf}})).status(),403);
  assert.equal((await context.request.post('/api/refresh',{headers:{Origin:origin,'x-csrf-token':session.csrf}})).status(),200);
  for (const width of [360,390,430,1440]) {
    await page.setViewportSize({width,height:900});
    for (const route of ['overview','bots','wethr','whiskeyjack','tasks','activity']) {
      await page.goto('/#'+route);
      await page.locator('footer').waitFor();
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${route} overflow at ${width}`);
    }
  }
  await page.evaluate(()=>navigator.serviceWorker.ready);
  await page.reload();
  const paths=await page.evaluate(async()=> (await Promise.all((await caches.keys()).map(async n=>(await (await caches.open(n)).keys()).map(r=>new URL(r.url).pathname)))).flat());
  assert.deepEqual(paths,['/offline.html']);
  await context.setOffline(true);
  await page.goto('/');
  await page.getByRole('heading',{name:'You’re offline'}).waitFor();
  await context.setOffline(false);
  assert.equal((await context.request.post('/api/logout',{headers:{Origin:origin,'x-csrf-token':session.csrf}})).status(),200);
  assert.equal((await context.request.get('/api/overview')).status(),401);
  assert.deepEqual(errors,[]);
  console.log('PASS: trusted HTTPS, authentication, secure cookie, origin/CSRF, real reads, worker heartbeat, all routes at four widths, offline-only cache and logout.');
} finally {
  await browser.close();
}
