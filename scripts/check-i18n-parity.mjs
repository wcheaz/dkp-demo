import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

function flattenKeys(obj, prefix = "") {
  const keys = [];
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) {
      keys.push(...flattenKeys(value, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

const en = JSON.parse(readFileSync(join(root, "src/i18n/messages/en.json"), "utf-8"));
const sk = JSON.parse(readFileSync(join(root, "src/i18n/messages/sk.json"), "utf-8"));

const enKeys = new Set(flattenKeys(en));
const skKeys = new Set(flattenKeys(sk));

const missingInSk = [...enKeys].filter((k) => !skKeys.has(k));
const missingInEn = [...skKeys].filter((k) => !enKeys.has(k));

if (missingInSk.length > 0) {
  console.error("Keys missing in sk.json:");
  missingInSk.forEach((k) => console.error(`  - ${k}`));
}

if (missingInEn.length > 0) {
  console.error("Keys missing in en.json:");
  missingInEn.forEach((k) => console.error(`  - ${k}`));
}

if (missingInSk.length > 0 || missingInEn.length > 0) {
  console.error(`\nParity check failed: ${missingInSk.length + missingInEn.length} mismatch(es) found.`);
  process.exit(1);
}

console.log(`i18n parity OK: ${enKeys.size} keys verified.`);
process.exit(0);
