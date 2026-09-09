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

// The browser's generic-font preferences are part of this Linux test
// environment. Named installed families avoid host-dependent empty defaults;
// this does not inject application CSS or modify the served document.
test.beforeEach(async ({page}) => {
  const session = await page.context().newCDPSession(page);
  await session.send('Page.setFontFamilies', {fontFamilies: {
    standard: 'DejaVu Sans', sansSerif: 'DejaVu Sans',
    serif: 'DejaVu Serif', fixed: 'DejaVu Sans Mono',
  }});
});

// A repository verification is asynchronous and can exceed the DOM assertion
// timeout on a slower machine. Await its actual response before inspecting UI.
async function openVerifiedPage(page) {
  const response = page.waitForResponse(r => new URL(r.url()).pathname === '/api/status');
  await page.goto('/');
  expect((await response).ok()).toBe(true);
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
  expect(api.dependency_ready_leaves).toEqual(["P9-2.1","P9-2.2","P9-2.3","P9-2.4","P9-2.5","P9-2.6","P9-3.1","P9-3.2","P9-3.3","P9-3.4","P9-3.5","P9-4.1","P9-4.2","P9-4.3","P9-4.4","P9-4.5","P9-4.6","P9-4.7a","P9-4.7b","P9-4.9.2","P9-7.2a-C_OS-NH-NH","P9-7.2a-C_OS-UNSUPPORTED","P9-7.2b-C_OS-MAPPED","P9-7.3-C_OS","P9-7.4-C_OS","P9-7.5-C_OS","P9-7.6-C_OS"]);
  expect(api.result_acceptance.accepted_iterations).toEqual(['P9-2.4']);
  expect(api.harness_acceptance.accepted_iterations).toEqual(['P9-2.5']);
  expect(api.integration_acceptance.accepted_iterations).toEqual(['P9-2.6']);
  expect(api.geometry_acceptance.accepted_iterations).toEqual(['P9-3.1']);
  expect(api.stage_acceptance.accepted_iterations).toEqual(['P9-3.2']);
  expect(api.resource_acceptance.accepted_iterations).toEqual(['P9-3.3']);
  expect(api.numerical_pressure_acceptance.accepted_iterations).toEqual(['P9-3.4']);
  expect(api.reference_transport_acceptance.accepted_iterations).toEqual(['P9-4.1']);
  expect(api.c_current_acceptance.accepted_iterations).toEqual(['P9-4.2']);
  expect(api.c_controls_acceptance.accepted_iterations).toEqual(['P9-4.3']);
  expect(api.os_pass_acceptance.accepted_iterations).toEqual(['P9-4.4']);
  expect(api.os_operations_acceptance.accepted_iterations).toEqual(['P9-4.5']);
  expect(api.lifecycle_batch_authorization.audit_status).toBe('findings_closed_after_correction');
  expect(api.lifecycle_batch_authorization.execution_order).toEqual(['P9-4.7a','P9-4.7b']);
  expect(api.preservation_acceptance.accepted_iterations).toEqual(['P9-3.5']);
  expect(api.permitted_runtime_paths).toHaveLength(29);
  expect(api.dependency_ready_leaves).toContain('P9-4.9.2');
  expect(api.receipt_parent_authority.policy_id).toBe('grcv4-previous-successful-primary-v1');
  expect(api.receipt_parent_authority.G2_accepted).toBe(false);
  expect(api.request_acceptance.accepted_iterations).toEqual(['P9-2.3']);
  expect(api.foundation_acceptance.accepted_iterations).toEqual(['P9-2.1','P9-2.2']);
  await openVerifiedPage(page);
  await expect(page.locator('#boundary')).toContainText('Passed');
  await page.locator('#parents-refresh').click();
  await expect(page.locator('#parents-status')).toContainText('Accepted policy: grcv4-previous-successful-primary-v1');
  const parentResponse = await page.request.get('/api/receipt-parents');
  const parentAPI = await parentResponse.json();
  expect(JSON.parse(await page.locator('#parents-output').textContent())).toEqual(parentAPI.claim);
  for (const key of ['debt','object','0','1','2']) {
    await page.locator('#parent-view').selectOption(key);
    expect(JSON.parse(await page.locator('#parents-output').textContent())).toEqual(['debt','object'].includes(key) ? parentAPI[key] : parentAPI.contracts[Number(key)]);
  }
  await page.route('**/api/receipt-parents', route => route.fulfill({status:503, body:'{}'}));
  await page.locator('#parents-refresh').click();
  await expect(page.locator('#parents-status')).toContainText('Held:');
  await expect(page.locator('#parents-output')).toBeEmpty();
  await page.unroute('**/api/receipt-parents');
  await page.evaluate(() => document.fonts.ready);
  const glyphs = await page.locator('h1').evaluate(element => {
    const canvas = document.createElement('canvas').getContext('2d');
    canvas.font = getComputedStyle(element).font;
    const width = canvas.measureText(element.textContent).width;
    return {width, height: element.getBoundingClientRect().height};
  });
  expect(glyphs.width, 'browser generic fonts must render actual glyphs').toBeGreaterThan(0);
  expect(glyphs.height, 'title text must occupy a visible line').toBeGreaterThan(0);

  await expect(page.locator('#iterations')).toContainText('P9-1.7');
  await expect(page.locator('#iterations')).toContainText('P9-1.8');
  await expect(page.locator('#iterations')).toContainText('P9-1.9');
  await expect(page.locator('#authority')).toContainText('Accepted / bounded implementation only');
  await expect(page.locator('#next-work')).toContainText('Accepted results: P9-2.4');
  await expect(page.locator('#next-work')).toContainText('Accepted harness: P9-2.5');
  await expect(page.locator('#next-work')).toContainText('Accepted integration: P9-2.6');
  await expect(page.locator('#next-work')).toContainText('P9-2.1, P9-2.2, P9-2.3, P9-2.4, P9-2.5, P9-2.6, P9-3.1, P9-3.2, P9-3.3, P9-3.4, P9-3.5, P9-4.1, P9-4.2, P9-4.3, P9-4.4, P9-4.5, P9-4.6');
  await expect(page.locator('#next-work')).toContainText('Accepted numerical pressure: P9-3.4');
  await expect(page.locator('#next-work')).toContainText('Accepted prestate preservation: P9-3.5');
  await expect(page.locator('#next-work')).toContainText('Accepted C reference transport: P9-4.1');
  await expect(page.locator('#next-work')).toContainText('Accepted C stage current: P9-4.2');
  await expect(page.locator('#next-work')).toContainText('Accepted C OS pass: P9-4.4');
  await expect(page.locator('#next-work')).toContainText('Accepted foundation: P9-2.1, P9-2.2.');
  await expect(page.locator('#next-work')).toContainText('Accepted after audit corrections: P9-4.6, P9-4.7a and P9-4.7b. Exact mapped vector verified under the successor release.');
  await expect(page.locator('#next-work')).toContainText('P9-4.9.2 parent authority accepted for implementation');
  await expect(page.locator('#next-work')).toContainText('P9-G2/G3 remain held');
  await expect(page.locator('#handoff')).toContainText('Verified');
  await expect(page.locator('#policy')).toContainText(api.policy_digest);
  await expect(page.locator('#sources')).toContainText(api.source_refs[0].sha256);
  const downloading = page.waitForEvent('download');
  await page.locator('#download').click();
  const download = await downloading;
  expect(JSON.parse(await readFile(await download.path(), 'utf8'))).toEqual(api);
  await page.screenshot({path: info.outputPath('verification.png'), fullPage: false});
  expect(await page.locator('h1').evaluate(e=>e.getBoundingClientRect().height)).toBeGreaterThan(0);
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
  for(const key of ['implementation_scope','dependency_ready_leaves','permitted_runtime_paths','foundation_acceptance','request_acceptance','result_acceptance','harness_acceptance','integration_acceptance','geometry_acceptance','stage_acceptance','resource_acceptance','numerical_pressure_acceptance','preservation_acceptance','reference_transport_acceptance','c_current_acceptance','c_controls_acceptance','os_pass_acceptance','os_operations_acceptance','lifecycle_batch_authorization','specification_correction','receipt_parent_authority','status_digest']) delete value[key];
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
  await openVerifiedPage(page);
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
  test.setTimeout(90000); // Two independently verified API subjects plus browser reads.
  await openVerifiedPage(page);
  await expect(page.locator('#source-meaning')).toContainText('indeterminate_requires_review');
  await expect(page.locator('#source-meaning')).toContainText('accepted_parent_successor_with_historical_crosswalk');
  for (const [id,decision] of [['normal_entry_forbidden_source','rejected'],['accepted_G1_exact_targets','admitted']]) {
    const api=await (await request.get(`/api/probe?case_id=${id}`)).json();
    const loaded=page.waitForResponse(r=>new URL(r.url()).searchParams.get('case_id')===id);
    await page.selectOption('#probe',id); // The change event performs the real refresh.
    await loaded;
    await expect(page.locator('#probe-candidate')).toHaveText(decision);
    await expect(page.locator('#probe-assertion')).toHaveText('passed');
    await expect(page.locator('#probe-status')).toContainText('no live permission');
    await expect(page.locator('#probe-subject')).toContainText(api.projection_digest);
    const pending=page.waitForEvent('download'); await page.locator('#probe-download').click();
    const file=await pending;
    expect(JSON.parse(await readFile(await file.path(),'utf8'))).toEqual(api);
    if (decision==='rejected') {
      await page.screenshot({path:info.outputPath('negative-assertion-not-admission.png'),fullPage:false});
      expect(await page.locator('#probe-candidate').evaluate(e=>e.getBoundingClientRect().height)).toBeGreaterThan(0);
    }
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
  await openVerifiedPage(page);
  await expect(page.locator('#boundary')).toContainText('Passed');
  const loaded=page.waitForResponse(r=>new URL(r.url()).searchParams.get('case_id')==='normal_entry_forbidden_source');
  await page.locator('#probe-refresh').click();
  await loaded;
  await expect(page.locator('#probe-candidate')).toHaveText('rejected');
  await page.route('**/api/probe?**',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.locator('#probe-refresh').click();
  await expect(page.locator('#probe-status')).toContainText('Held:');
  await expect(page.locator('#probe-candidate')).toHaveText('Not loaded');
  await expect(page.locator('#probe-assertion')).toHaveText('Not loaded');
  await expect(page.locator('#probe-download')).toBeDisabled();
});
