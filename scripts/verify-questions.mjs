// Isolated Vite server on 5175; all API responses are synthetic, no bot access.
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';

const at='2026-09-18T10:00:00+00:00';
const malicious='<img src=x onerror="window.sourceTextExecuted=true">';
const records=[
  {title:'Will the synthetic launch occur by Friday?',kind:'binary',rows:[{label:'Yes',value:0},{label:'No',value:1}]},
  {title:'Which team will win the synthetic event?',kind:'multiple_choice',rows:[{label:'North',value:.2},{label:'South',value:.8}]},
  {title:'What will the synthetic measurement be?',kind:'numeric',rows:[{label:'10th percentile',value:-5},{label:'50th percentile',value:10},{label:'90th percentile',value:120}],unit:'units'},
  {title:malicious,kind:'discrete',rows:[{label:'50th percentile',value:7}],unit:'items'},
].map((r,i)=>({id:`fixture-${i}`,question_id:i+1,title:r.title,group_title:i===2?'Synthetic monthly measurements':null,
  type:r.kind,status:'validated',resolution:'unresolved',scores:[],at,uncertainties:0,
  question_details:{background:malicious,resolution_criteria:'Use the synthetic official result.',fine_print:null},
  forecast:{kind:r.kind,rows:r.rows,unit:r.unit||null,version:2,generated_at:at,as_of:'2026-09-17T10:00:00+00:00'},
  community:{status:'unavailable',observed_at:null,reason:'No community prediction is stored in this synthetic fixture.'},
}));
const browser=await chromium.launch({executablePath:process.env.PASSERINE_CHROMIUM||undefined});
try {
  const page=await browser.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/**',async route=>{
    const body=route.request().url().endsWith('/session')?{csrf:'synthetic'}:{
      sources:[{id:'whiskeyjack',connection:'connected',collected_at:at,attempt_at:at,cache_stale:false,error:null,
        observation:{origin:'demo',source_observed_at:at,heartbeat_at:null,job_success_at:null,coverage:'Synthetic fixture',data:{records}}}],
      events:[],incidents:[],outbox:[],worker:{alive:true,heartbeat:at},
    };
    await route.fulfill({json:body});
  });
  for(const width of [360,390,430,1440]) {
    await page.setViewportSize({width,height:900});
    await page.goto('http://127.0.0.1:5175/#whiskeyjack');
    await page.getByRole('heading',{name:records[0].title,exact:true}).waitFor();
    const cards=page.locator('.records article');
    assert.equal(await cards.count(),4);
    assert.match(await cards.nth(0).innerText(),/0%/);
    assert.match(await cards.nth(1).innerText(),/80%/);
    assert.match(await cards.nth(2).innerText(),/Recorded percentiles · units/);
    assert.equal(await page.getByText('Community unavailable.',{exact:true}).count(),4);
    assert.equal(await page.locator('.records img').count(),0);
    const details=cards.nth(0).locator('details');
    if(!await details.evaluate(element=>element.open)) {
      await cards.nth(0).getByText('Question details at forecast time',{exact:true}).click();
    }
    await cards.nth(0).getByRole('heading',{name:'Background',exact:true}).waitFor();
    assert.match(await cards.nth(0).innerText(),/<img src=x/);
    assert.equal(await page.evaluate(()=>window.sourceTextExecuted),undefined);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    if(width===390) {
      await cards.nth(0).scrollIntoViewIfNeeded();
      await mkdir('runtime/screenshots',{recursive:true});
      await page.screenshot({path:'runtime/screenshots/questions-mobile.png'});
    }
  }
  assert.deepEqual(errors,[]);
  console.log('PASS: question titles, all four forecast types, zero probability, unavailable community, escaped source text and no overflow at four widths.');
} finally {await browser.close();}
