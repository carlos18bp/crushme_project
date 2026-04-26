#!/usr/bin/env node
/**
 * Fails if flow-definitions.json and the e2e/ @flow: usage diverge.
 *
 * Two extraction modes (additive, whichever matches):
 *   1. Literal `@flow:<id>` occurrences in any .ts/.js file (used by most projects).
 *   2. `FlowIds = Object.freeze({ key: '<id>', ... })` helper blocks — kebab-case
 *      string values count as referenced flow IDs. Covers projects where tags are
 *      built at runtime (e.g. `FlowTags.flows.X`) so the literal `@flow:<id>`
 *      never appears statically.
 *
 * Usage: node frontend/scripts/check-flow-definitions-sync.mjs [--definitions <path>] [--e2e-dir <path>]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FLOW_TAG_RE = /@flow:([a-z0-9-]+)/g;
const FLOW_IDS_BLOCK_RE = /FlowIds\s*=\s*Object\.freeze\(\s*\{([\s\S]*?)\}\s*\)/;
const KEBAB_STRING_RE = /['"]([a-z0-9]+(?:-[a-z0-9]+)*)['"]/g;

function parseArgs(argv) {
  const frontendRoot = path.resolve(__dirname, '..');
  let definitionsPath = path.join(frontendRoot, 'e2e', 'flow-definitions.json');
  let e2eDir = path.join(frontendRoot, 'e2e');
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--definitions' && argv[i + 1]) definitionsPath = path.resolve(argv[++i]);
    else if (argv[i] === '--e2e-dir' && argv[i + 1]) e2eDir = path.resolve(argv[++i]);
  }
  return { definitionsPath, e2eDir };
}

function collectSourceFiles(dir, acc = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) collectSourceFiles(full, acc);
    else if (ent.isFile() && (ent.name.endsWith('.ts') || ent.name.endsWith('.js'))) acc.push(full);
  }
  return acc;
}

function collectTagIds(e2eDir) {
  const ids = new Set();
  for (const file of collectSourceFiles(e2eDir)) {
    const text = fs.readFileSync(file, 'utf8');
    for (const [, id] of text.matchAll(FLOW_TAG_RE)) ids.add(id);
    const block = text.match(FLOW_IDS_BLOCK_RE);
    if (block) {
      for (const [, id] of block[1].matchAll(KEBAB_STRING_RE)) ids.add(id);
    }
  }
  return ids;
}

const { definitionsPath, e2eDir } = parseArgs(process.argv);
const data = JSON.parse(fs.readFileSync(definitionsPath, 'utf8'));
const flows = data.flows ?? {};
const definedIds = new Set(Object.keys(flows));
const taggedIds = collectTagIds(e2eDir);

const unknownTags = [...taggedIds].filter((id) => !definedIds.has(id)).sort();
const missingCoverage = Object.entries(flows)
  .filter(([, def]) => (def?.expectedSpecs ?? 1) !== 0)
  .map(([id]) => id)
  .filter((id) => !taggedIds.has(id))
  .sort();

let failed = false;
if (unknownTags.length) {
  failed = true;
  console.error(`\n❌ @flow: IDs in e2e/ missing from flow-definitions.json (${unknownTags.length}):\n`);
  unknownTags.forEach((id) => console.error(`   - ${id}`));
}
if (missingCoverage.length) {
  failed = true;
  console.error(`\n❌ Flows in flow-definitions.json with no @flow: tag in e2e/ (${missingCoverage.length}):\n`);
  missingCoverage.forEach((id) => console.error(`   - ${id}  (${flows[id]?.name ?? id})`));
}
if (failed) {
  console.error('\nFix: add missing definitions or tags, or set expectedSpecs: 0 for intentionally uncovered flows.\n');
  process.exit(1);
}
console.log(`✅ flow-definitions.json ↔ e2e @flow: tags in sync (${taggedIds.size} tagged, ${definedIds.size} defined).\n`);
