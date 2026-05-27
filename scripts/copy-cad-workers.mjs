import { readdir, copyFile, mkdir, realpath } from "node:fs/promises";
import { basename, join } from "node:path";

const MLIGHT_DIR = "node_modules/@mlightcad";
const OUTPUT_DIR = "public/workers";

async function walkDir(dir) {
  const workerFiles = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return workerFiles;
  }

  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      const sub = await walkDir(fullPath);
      workerFiles.push(...sub);
    } else if (entry.isFile() && entry.name.includes("worker") && entry.name.endsWith(".js")) {
      workerFiles.push(fullPath);
    } else if (entry.isSymbolicLink()) {
      try {
        const realPath = await realpath(fullPath);
        const stat = await import("node:fs/promises").then((m) => m.stat(realPath));
        if (stat.isDirectory()) {
          const sub = await walkDir(realPath);
          workerFiles.push(...sub);
        } else if (stat.isFile() && entry.name.includes("worker") && entry.name.endsWith(".js")) {
          workerFiles.push(realPath);
        }
      } catch {
        // broken symlink, skip
      }
    }
  }

  return workerFiles;
}

async function main() {
  let mlightEntries;
  try {
    mlightEntries = await readdir(MLIGHT_DIR, { withFileTypes: true });
  } catch {
    console.error(
      "Error: cad-simple-viewer – node_modules/@mlightcad/ not found. Run pnpm install first."
    );
    process.exit(1);
  }

  const allWorkerFiles = [];

  for (const entry of mlightEntries) {
    const fullPath = join(MLIGHT_DIR, entry.name);
    if (entry.isDirectory()) {
      const files = await walkDir(fullPath);
      allWorkerFiles.push(...files);
    } else if (entry.isSymbolicLink()) {
      try {
        const realPath = await realpath(fullPath);
        const files = await walkDir(realPath);
        allWorkerFiles.push(...files);
      } catch {
        // broken symlink, skip
      }
    }
  }

  if (allWorkerFiles.length === 0) {
    console.error(
      "Error: cad-simple-viewer – no worker files found in node_modules/@mlightcad/. " +
        "Expected files matching *worker*.js."
    );
    process.exit(1);
  }

  await mkdir(OUTPUT_DIR, { recursive: true });

  for (const filePath of allWorkerFiles) {
    const dest = join(OUTPUT_DIR, basename(filePath));
    await copyFile(filePath, dest);
    console.log(`Copied: ${basename(filePath)}`);
  }

  console.log(`Done: ${allWorkerFiles.length} worker file(s) copied to ${OUTPUT_DIR}/`);
}

main().catch((err) => {
  console.error("Error copying cad-simple-viewer worker files:", err.message);
  process.exit(1);
});
