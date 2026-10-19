import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
const root = process.cwd();
const ignored = new Set([
  "node_modules",
  "dist",
  "coverage",
  "test-results",
  ".git",
]);
const extensions = new Set([
  ".ts",
  ".js",
  ".json",
  ".yml",
  ".yaml",
  ".md",
  ".html",
  ".css",
]);
const secret =
  /(api[_-]?key|password|secret|token|passwd)\s*[:=]\s*["'][^"']{8,}["']/i;
let matches = [];
function walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (ignored.has(entry)) continue;
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) walk(path);
    else if (extensions.has(path.slice(path.lastIndexOf(".")))) {
      const text = readFileSync(path, "utf8");
      if (secret.test(text)) matches.push(path);
    }
  }
}
walk(root);
if (matches.length) {
  console.error(`Potential secrets in: ${matches.join(", ")}`);
  process.exit(1);
}
console.log(
  "secret-scan: 0 findings (generated/dependency directories excluded)",
);
