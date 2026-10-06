// Focused real HTTP/DOM check. The separate full phase status is checked elsewhere.
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import {TRANCHE8_EVIDENCE as expected} from './tranche8-evidence.js';
const require=createRequire(new URL('../web/package.json',import.meta.url));
const {chromium}=require('@playwright/test');
const base=process.env.PHASE9_TEST_URL;
if(!base) throw new Error('PHASE9_TEST_URL must name the local test server');
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage();
  page.setDefaultTimeout(30000);
  page.setDefaultNavigationTimeout(30000);
  // Do not trigger the costly, independent whole-history status check twice.
  await page.route('**/api/status', route=>route.fulfill({status:503,contentType:'application/json',body:'{"error":"separate full-boundary check not requested by this focused test"}'}));
  const response=page.waitForResponse(r=>r.url()===base+'/api/tranche8',{timeout:120000});
  // Preserve an earlier navigation/font failure when cleanup rejects this wait.
  response.catch(()=>{});
  await page.goto(base);
  assert.ok(await page.locator('h1').evaluate(e => e.getBoundingClientRect().height > 0),
    'Browser font environment renders zero-height text; repair font configuration before UI verification');
  const network=await response;assert.equal(network.status(),200);const value=await network.json();
  console.log('TRANCHE8_BROWSER_CHECK status_received=true');
  await page.locator('#tranche8-status').filter({hasText:'Retained sources checked'}).waitFor({timeout:15000});
  const content=await page.locator('#tranche8-evidence').innerText();
  const counts = `${expected.coverage.accepted_cells}/${expected.coverage.required_cells}`;
  for(const s of [counts,`${expected.coverage.pending_cells} pending`,'C_RG2b','A_RG2b','A_CI_PC','Larger configurations']) assert.ok(content.includes(s),s);
  assert.deepEqual(value.coverage, expected.coverage);
  const ref=value.profiles.find(r=>r.family==='C_PC').review;
  const source=await page.request.get(base+'/api/tranche8/source?path='+encodeURIComponent(ref.path),{timeout:120000});
  assert.equal(source.status(),200);assert.equal(source.headers()['x-evidence-sha256'],ref.sha256);
  assert.ok((await source.text()).includes('P9-8.3C-PC whole-carrier event integration'));
  console.log('TRANCHE8_BROWSER_CHECK accepted_source_received=true');
  for (const run of expected.coverage.runs.filter(r=>r.acceptance===null)) {
    const pending=await page.request.get(base+'/api/tranche8/source?path='+encodeURIComponent(run.review.path),{timeout:120000});
    assert.equal(pending.status(),200);assert.equal(pending.headers()['x-evidence-sha256'],run.review.sha256);
    console.log('TRANCHE8_BROWSER_CHECK pending_source_received='+run.family);
    await page.locator('#tranche8-evidence > details > summary').filter({hasText:run.results.path.split('/').at(-1)}).click();
    assert.ok((await page.locator('#tranche8-evidence').innerText()).includes('No accepted coverage credited'));
  }
  const invalid=await page.request.get(base+'/api/tranche8/source?path=../secret',{timeout:120000});assert.equal(invalid.status(),404);
  await page.route('**/api/tranche8',route=>route.fulfill({contentType:'application/json',body:JSON.stringify(value)}));
  await page.setViewportSize({width:390,height:844});
  await page.locator('#tranche8-refresh').click();
  await page.locator('#tranche8-status').filter({hasText:'Retained sources checked'}).waitFor();
  assert.ok((await page.locator('#tranche8-evidence').innerText()).includes(counts));
  await page.unroute('**/api/tranche8');
  await page.route('**/api/tranche8',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.locator('#tranche8-refresh').click();
  await page.locator('#tranche8-status').filter({hasText:'Unavailable'}).waitFor();
  assert.equal(await page.locator('#tranche8-evidence').innerText(),'');
  console.log('TRANCHE8_BROWSER_PASS real_HTTP_sources=true desktop_mobile=true failed_refresh_cleared=true native_rerun=false');
} finally {await browser.close();}
