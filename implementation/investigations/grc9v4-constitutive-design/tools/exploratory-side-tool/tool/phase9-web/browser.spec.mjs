import { test, expect } from '../web/node_modules/@playwright/test/index.mjs';
import { readFile } from 'node:fs/promises';

test('live API, source bindings, leaf states and downloadable JSON agree', async ({page, request}, info) => {
  const response = await request.get('/api/status');
  expect(response.headers()['cache-control']).toBe('no-store');
  const api = await response.json();
  expect(api.current_boundary).toBe('passed');
  expect(api.runtime_authorized).toBe(false);
  await page.goto('/');
  await expect(page.locator('#boundary')).toContainText('Passed');
  await expect(page.locator('#iterations')).toContainText('P9-1.7');
  await expect(page.locator('#iterations')).toContainText('P9-1.8');
  await expect(page.locator('#policy')).toContainText(api.policy_digest);
  await expect(page.locator('#sources')).toContainText(api.source_refs[0].sha256);
  const downloading = page.waitForEvent('download');
  await page.locator('#download').click();
  const download = await downloading;
  expect(JSON.parse(await readFile(await download.path(), 'utf8'))).toEqual(api);
  await page.screenshot({path: info.outputPath('verification.png'), fullPage: true});
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('refresh failure removes stale success and disables download', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#boundary')).toContainText('Passed');
  await page.route('**/api/status', route => route.fulfill({status: 503, body: 'unavailable'}));
  await page.locator('#refresh').click();
  await expect(page.locator('#status')).toContainText('Held:');
  await expect(page.locator('#boundary')).toHaveText('Not verified');
  await expect(page.locator('#download')).toBeDisabled();
  await expect(page.locator('#sources')).toBeEmpty();
});

test('forged runtime payload and changed digest fail closed', async ({page, request}) => {
  const original = await (await request.get('/api/status')).json();
  for (const patch of [{runtime_authorized: true}, {claim_ceiling: 'forged claim'}]) {
    await page.route('**/api/status', route => route.fulfill({contentType: 'application/json', body: JSON.stringify({...original, ...patch})}));
    await page.goto('/');
    await expect(page.locator('#status')).toContainText('Held:');
    await expect(page.locator('#download')).toBeDisabled();
    await page.unroute('**/api/status');
  }
});

test('server exposes no write or arbitrary repository read route', async ({request}) => {
  expect((await request.post('/api/status', {data: {runtime_authorized: true}})).status()).toBe(405);
  expect((await request.get('/pyproject.toml')).status()).toBe(404);
  expect((await request.get('/api/run-verification')).status()).toBe(404);
});

test('actual negative assertion and future fixture keep their subjects through UI and export', async ({page, request}, info) => {
  await page.goto('/');
  await expect(page.locator('#source-meaning')).toContainText('indeterminate_requires_review');
  await expect(page.locator('#source-meaning')).toContainText('accepted_frozen');
  for (const [id,decision] of [['normal_entry_forbidden_source','rejected'],['future_explicit_approval_exact_targets','admitted']]) {
    const api=await (await request.get(`/api/probe?case_id=${id}`)).json();
    await page.selectOption('#probe',id);
    await page.locator('#probe-refresh').click();
    await expect(page.locator('#probe-candidate')).toHaveText(decision);
    await expect(page.locator('#probe-assertion')).toHaveText('passed');
    await expect(page.locator('#probe-status')).toContainText('no live permission');
    await expect(page.locator('#probe-subject')).toContainText(api.projection_digest);
    const pending=page.waitForEvent('download'); await page.locator('#probe-download').click();
    const file=await pending;
    expect(JSON.parse(await readFile(await file.path(),'utf8'))).toEqual(api);
    if (decision==='rejected') await page.screenshot({path:info.outputPath('negative-assertion-not-admission.png'),fullPage:true});
  }
});

test('older subject A finishing after B cannot overwrite B', async ({page,request}) => {
  const a=await (await request.get('/api/probe?case_id=normal_entry_forbidden_source')).json();
  const b=await (await request.get('/api/probe?case_id=future_explicit_approval_exact_targets')).json();
  let releaseA, seenA;
  const started=new Promise(resolve=>{seenA=resolve;});
  const release=new Promise(resolve=>{releaseA=resolve;});
  await page.route('**/api/probe?**',async route=>{
    if (route.request().url().includes('normal_entry_forbidden_source')) {seenA();await release;await route.fulfill({json:a});}
    else await route.fulfill({json:b});
  });
  await page.goto('/');await page.locator('#probe-refresh').click();await started;
  await page.selectOption('#probe','future_explicit_approval_exact_targets');
  await expect(page.locator('#probe-candidate')).toHaveText('admitted');
  releaseA();
  await page.waitForResponse(r=>r.url().includes('normal_entry_forbidden_source'));
  await expect(page.locator('#probe-subject')).toContainText(b.case_id);
  await expect(page.locator('#probe-candidate')).toHaveText('admitted');
});

test('failed probe refresh clears assertion and candidate; unknown full ID is not a neighbor', async ({page,request}) => {
  expect((await request.get('/api/probe?case_id=normal_entry_forbidden_source-unknown')).status()).toBe(404);
  await page.goto('/');await page.locator('#probe-refresh').click();
  await expect(page.locator('#probe-candidate')).toHaveText('rejected');
  await page.route('**/api/probe?**',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.locator('#probe-refresh').click();
  await expect(page.locator('#probe-status')).toContainText('Held:');
  await expect(page.locator('#probe-candidate')).toHaveText('Not loaded');
  await expect(page.locator('#probe-assertion')).toHaveText('Not loaded');
  await expect(page.locator('#probe-download')).toBeDisabled();
});
