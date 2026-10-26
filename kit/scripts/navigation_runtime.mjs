import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const [adapterPath, scenarioPath] = process.argv.slice(2);
const adapter = JSON.parse(await readFile(adapterPath, 'utf8'));
const scenario = JSON.parse(await readFile(scenarioPath, 'utf8'));
const issues = [];
const observations = [];
const hosts = new Set(scenario.allowed_hosts ?? adapter.allowed_hosts ?? []);
const allowed = new Set(scenario.allowed_statuses ?? []);
const issue = (code, message, path = '$') => issues.push({code, message, path});
const modulePath = process.env.BOTTEGA_PLAYWRIGHT_MODULE || adapter.playwright_module;
if (!modulePath) { console.log(JSON.stringify({schema_version:'guardrails/v1',verdict:'BLOCKED',exit_code:3,issues:[{code:'NAV_RUNTIME',message:'Playwright module is unavailable',path:'$'}],mode:'read-only',observations:[]})); process.exit(3); }
try {
  const { chromium } = await import(pathToFileURL(modulePath).href);
  const browser = await chromium.launch({headless:true, executablePath: adapter.chromium_executable});
  const context = await browser.newContext();
  for (const [name, envName] of Object.entries(adapter.auth_cookie_bindings ?? {})) {
    const value = process.env[envName];
    if (!value) throw new Error(`missing auth cookie binding: ${envName}`);
    await context.addCookies([{name, value, url: adapter.base_url}]);
  }
  const page = await context.newPage();
  page.on('request', req => {
    const url = new URL(req.url());
    observations.push({kind:'request',host:url.hostname,method:req.method(),path:url.pathname + url.search});
    if (!hosts.has(url.hostname)) issue('NAV003','external host denied','requests');
  });
  page.on('response', response => {
    const url = new URL(response.url());
    if (allowed.has(response.status())) return;
    const ok = (scenario.known_errors ?? []).some(x => x?.status === response.status() && x?.path === url.pathname && x?.decision_ref);
    if (!ok) issue('NAV002','status not allowlisted',`responses.${url.pathname}`);
  });
  const start = new URL(scenario.canonical_start ?? '/login', adapter.base_url).href;
  const response = await page.goto(start, {waitUntil:'networkidle', timeout: Number(adapter.timeout_ms ?? 10000)});
  if (!response || !allowed.has(response.status())) issue('NAV002','canonical start status not allowlisted');
  for (const step of adapter.canonical_steps ?? []) {
    if (step?.action !== 'click' || typeof step.selector !== 'string' || !/^[#.[].+/.test(step.selector)) { issue('NAV004','only declared CSS click selectors are allowed','canonical_steps'); continue; }
    await page.locator(step.selector).click({timeout:3000});
    await page.waitForLoadState('networkidle');
  }
  const final = new URL(page.url());
  if (!hosts.has(final.hostname)) issue('NAV003','final host not allowlisted');
  observations.push({kind:'final',status:response?.status() ?? null,path:final.pathname + final.search});
  await context.close(); await browser.close();
  const report={schema_version:'guardrails/v1',verdict:issues.length?'FAIL':'PASS',exit_code:issues.length?1:0,issues,mode:'read-only',observations};
  console.log(JSON.stringify(report)); process.exit(report.exit_code);
} catch (error) {
  const report={schema_version:'guardrails/v1',verdict:'FAIL',exit_code:1,issues:[{code:'NAV000',message:error?.name ?? 'runtime error',path:'$'}],mode:'read-only',observations};
  console.log(JSON.stringify(report)); process.exit(1);
}
