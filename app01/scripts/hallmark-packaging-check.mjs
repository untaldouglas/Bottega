import { existsSync, readdirSync, statSync, readFileSync } from "node:fs";
import { join } from "node:path";

const appRoot = process.cwd();
const forbidden =
  /(^|\/)(automation|project-evidence|evidence|\.env|logs?|caches?|coverage|playwright-report|test-results|tests|node_modules)(\/|$)|\.log$/i;
const failures = [];
const assert = (condition, message) => {
  if (!condition) failures.push(message);
};
assert(!existsSync(join(appRoot, "automation")), "source contiene automation/");
const walk = (dir, prefix = "") => {
  if (!existsSync(dir)) return;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const path = `${prefix}${entry}`;
    if (forbidden.test(path))
      failures.push(`ruta prohibida en artefacto: ${path}`);
    if (statSync(full).isDirectory()) walk(full, `${path}/`);
  }
};
walk(join(appRoot, "dist"));
assert(existsSync(join(appRoot, "dist/index.html")), "dist/index.html ausente");
assert(existsSync(join(appRoot, "server.mjs")), "server.mjs ausente");
const runtimeText = readFileSync(join(appRoot, "server.mjs"), "utf8");
assert(
  !/automation|TELEGRAM_BOT_TOKEN|\.env(?:$|[/\\])/i.test(runtimeText),
  "runtime referencia expediente o secreto",
);
const packageText = readFileSync(join(appRoot, "package.json"), "utf8");
assert(
  !/automation|project-evidence|\.env/i.test(packageText),
  "package distribuible referencia expediente o secreto",
);
if (failures.length) {
  console.error(JSON.stringify({ ok: false, failures }, null, 2));
  process.exit(1);
}
console.log(
  JSON.stringify(
    {
      ok: true,
      source: appRoot,
      dist: join(appRoot, "dist"),
      runtime: "server.mjs",
    },
    null,
    2,
  ),
);
