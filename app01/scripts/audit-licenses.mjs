import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
const root = join(process.cwd(), "node_modules");
const licenses = new Map();
function walk(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (
      entry.isDirectory() &&
      (entry.name.startsWith("@") || !entry.name.startsWith("."))
    ) {
      if (entry.name.startsWith("@")) walk(path);
      else {
        const pkg = join(path, "package.json");
        try {
          const data = JSON.parse(readFileSync(pkg, "utf8"));
          const license =
            typeof data.license === "string"
              ? data.license
              : (data.license?.type ?? "UNKNOWN");
          licenses.set(`${data.name}@${data.version}`, license);
        } catch {
          walk(path);
        }
      }
    }
  }
}
walk(root);
const unknown = [...licenses].filter(([, license]) => license === "UNKNOWN");
console.log(`license-inventory: ${licenses.size} packages`);
console.log(`license-inventory: ${unknown.length} unknown licenses`);
if (unknown.length) {
  console.error(unknown.map(([name]) => name).join("\n"));
  process.exit(1);
}
