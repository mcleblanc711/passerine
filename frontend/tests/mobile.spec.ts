import {test,expect} from '@playwright/test';
for(const width of [360,390,430,1440]){
 test(`navigation and layout ${width}px`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width,height:900});
  await page.goto('/');
  await page.getByLabel('Private access password').fill('local-verification-only');
  await page.getByRole('button',{name:'Open Passerine'}).click();
  await expect(page.getByRole('heading',{name:'A view from the perch.'})).toBeVisible();
  await page.screenshot({path:`../runtime/screenshots/overview-${width}.png`,fullPage:true});
  for(const route of ['bots','wethr','whiskeyjack','tasks','activity','overview']){
    await page.goto('/#'+route);
    await expect(page.locator('footer')).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  }
  await page.goto('/#wethr');
  await page.getByRole('combobox').selectOption('all');
  await expect(page.getByText('$15.00',{exact:true})).toBeVisible();
  await expect(page.getByText('$105.00',{exact:true})).toBeVisible();
  await page.goto('/#whiskeyjack');
  await expect(page.getByText('withheld',{exact:true})).toBeVisible();
  await expect(page.getByText('Awaiting local score',{exact:true})).toBeVisible();
  expect(errors).toEqual([]);
 });
}
test('offline screen and no private persistent cache',async({page,context})=>{
 await page.goto('/');
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await page.reload();
 const cachePaths=await page.evaluate(async()=>{const names=await caches.keys();return (await Promise.all(names.map(async n=>(await (await caches.open(n)).keys()).map(r=>new URL(r.url).pathname)))).flat()});
 expect(cachePaths).toEqual(['/offline.html']);
 await context.setOffline(true);
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'You’re offline'})).toBeVisible();
});
