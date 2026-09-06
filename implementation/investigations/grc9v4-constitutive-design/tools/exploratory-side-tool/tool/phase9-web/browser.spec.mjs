import { test, expect } from '../web/node_modules/@playwright/test/index.mjs';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

// Independent status-fixture serialization; do not import browser code through
// Playwright's CommonJS loader or use the implementation as its own oracle.
function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  return JSON.stringify(value);
}

test('live API, source bindings, leaf states and downloadable JSON agree', async ({page, request}, info) => {
  const response = await request.get('/api/status');
  expect(response.headers()['cache-control']).toBe('no-store');
  const api = await response.json();
  expect(api.current_boundary).toBe('passed');
  expect(api.runtime_authorized).toBe(true);
  expect(api.P9_G1_accepted).toBe(true);
  expect(api.accepted_generic_runtime_support).toEqual([]);
  expect(api.admitted_specialization_support_sets).toEqual([]);
  expect(api.dependency_ready_leaves).toEqual(['P9-2.1','P9-2.2','P9-2.3','P9-2.4','P9-2.5','P9-2.6']);
  expect(api.result_acceptance.accepted_iterations).toEqual(['P9-2.4']);
  expect(api.harness_acceptance.accepted_iterations).toEqual(['P9-2.5']);
  expect(api.request_acceptance.accepted_iterations).toEqual(['P9-2.3']);
  expect(api.foundation_acceptance.accepted_iterations).toEqual(['P9-2.1','P9-2.2']);
  await page.goto('/');
  await expect(page.locator('#boundary')).toContainText('Passed');
  await expect(page.locator('#iterations')).toContainText('P9-1.7');
  await expect(page.locator('#iterations')).toContainText('P9-1.8');
  await expect(page.locator('#iterations')).toContainText('P9-1.9');
  await expect(page.locator('#authority')).toContainText('Accepted / bounded implementation only');
  await expect(page.locator('#next-work')).toContainText('Accepted results: P9-2.4');
  await expect(page.locator('#next-work')).toContainText('Accepted harness: P9-2.5');
  await expect(page.locator('#next-work')).toContainText('P9-2.1, P9-2.2, P9-2.3, P9-2.4, P9-2.5, P9-2.6');
  await expect(page.locator('#next-work')).toContainText('Accepted foundation: P9-2.1, P9-2.2.');
  await expect(page.locator('#handoff')).toContainText('Verified');
  await expect(page.locator('#policy')).toContainText(api.policy_digest);
  await expect(page.locator('#sources')).toContainText(api.source_refs[0].sha256);
  const downloading = page.waitForEvent('download');
  await page.locator('#download').click();
  const download = await downloading;
  expect(JSON.parse(await readFile(await download.path(), 'utf8'))).toEqual(api);
  await page.screenshot({path: info.outputPath('verification.png'), fullPage: true});
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('archive availability is visible without revoking acceptance or blocking export', async ({page,request}) => {
  const original=await (await request.get('/api/status')).json();
  for(const [status,label] of [['unavailable','Unavailable'],['invalid','Invalid']]) {
    const value={...original,handoff_evidence:{status}};
    delete value.status_digest;
    value.status_digest=createHash('sha256').update(canonical(value)).digest('hex');
    await page.route('**/api/status', route=>route.fulfill({json:value}));
    await page.goto('/');
    await expect(page.locator('#handoff')).toContainText(label);
    await expect(page.locator('#authority')).toContainText('Accepted / bounded implementation only');
    await expect(page.locator('#boundary')).toContainText('Passed');
    const pending=page.waitForEvent('download'); await page.locator('#download').click();
    const file=await pending;
    expect(JSON.parse(await readFile(await file.path(),'utf8'))).toEqual(value);
    await page.unroute('**/api/status');
  }
});

test('a current source failure holds work but preserves the recorded acceptance display', async ({page,request}) => {
  const value=await (await request.get('/api/status')).json();
  Object.assign(value,{current_boundary:'failed_closed',runtime_authorized:false,runtime_authority_state:'accepted_P9_G1_current_work_held',recorded_full_verification:'not_current',source_refs:[],iterations:[],policy_digest:null,error:'Current source binding failed'});
  for(const key of ['implementation_scope','dependency_ready_leaves','permitted_runtime_paths','foundation_acceptance','request_acceptance','result_acceptance','harness_acceptance','status_digest']) delete value[key];
  value.status_digest=createHash('sha256').update(canonical(value)).digest('hex');
  await page.route('**/api/status',route=>route.fulfill({json:value}));
  await page.goto('/');
  await expect(page.locator('#boundary')).toContainText('Failed');
  await expect(page.locator('#authority')).toHaveText('Accepted / current work held');
  await expect(page.locator('#status')).toContainText('acceptance remains intact');
  await expect(page.locator('#next-work')).toContainText('Current work held');
  await expect(page.locator('#download')).toBeEnabled();
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
  await expect(page.locator('#authority')).toHaveText('Not verified / permission withheld');
  await expect(page.locator('#next-work')).toHaveText('Next work not verified.');
});

test('forged runtime payload and changed digest fail closed', async ({page, request}) => {
  const original = await (await request.get('/api/status')).json();
  for (const patch of [{runtime_authorized: false}, {accepted_generic_runtime_support: ['C_OS']}, {claim_ceiling: 'forged claim'}]) {
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
  for (const [id,decision] of [['normal_entry_forbidden_source','rejected'],['accepted_G1_exact_targets','admitted']]) {
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
  const b=await (await request.get('/api/probe?case_id=accepted_G1_exact_targets')).json();
  let releaseA, seenA;
  const started=new Promise(resolve=>{seenA=resolve;});
  const release=new Promise(resolve=>{releaseA=resolve;});
  await page.route('**/api/probe?**',async route=>{
    if (route.request().url().includes('normal_entry_forbidden_source')) {seenA();await release;await route.fulfill({json:a});}
    else await route.fulfill({json:b});
  });
  await page.goto('/');await page.locator('#probe-refresh').click();await started;
  await page.selectOption('#probe','accepted_G1_exact_targets');
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
