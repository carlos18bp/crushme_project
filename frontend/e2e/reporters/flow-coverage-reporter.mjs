import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const _file = fileURLToPath(import.meta.url);
const _dir = path.dirname(_file);

class FlowCoverageReporter {
  flowStats = new Map();
  unmappedTests = [];
  outputDir;

  constructor(options = {}) {
    this.outputDir = options.outputDir || 'e2e-results';

    const definitionsPath = path.resolve(_dir, '..', 'flow-definitions.json');
    if (fs.existsSync(definitionsPath)) {
      this.flowDefinitions = JSON.parse(fs.readFileSync(definitionsPath, 'utf-8'));
    } else {
      this.flowDefinitions = { version: '0.0.0', lastUpdated: '', flows: {} };
      console.warn('\n  ⚠️  flow-definitions.json not found.\n');
    }

    for (const [flowId, definition] of Object.entries(this.flowDefinitions.flows)) {
      this.flowStats.set(flowId, {
        flowId,
        definition,
        tests: { total: 0, passed: 0, failed: 0, skipped: 0 },
        specs: new Set(),
        status: 'missing',
      });
    }
  }

  onTestEnd(test, result) {
    const tags = test.tags || [];
    const flowTags = tags.filter((t) => t.startsWith('@flow:'));
    const specFile = test.location.file;

    if (flowTags.length === 0) {
      this.unmappedTests.push({ title: test.title, file: specFile });
      return;
    }

    for (const tag of flowTags) {
      const flowId = tag.replace('@flow:', '');
      let stats = this.flowStats.get(flowId);
      if (!stats) {
        stats = {
          flowId,
          definition: { name: flowId, module: 'unknown', roles: ['unknown'], priority: 'P4', description: 'Auto-detected', expectedSpecs: 1 },
          tests: { total: 0, passed: 0, failed: 0, skipped: 0 },
          specs: new Set(),
          status: 'missing',
        };
        this.flowStats.set(flowId, stats);
      }

      stats.tests.total++;
      stats.specs.add(specFile);

      if (result.status === 'passed') stats.tests.passed++;
      else if (result.status === 'failed' || result.status === 'timedOut') stats.tests.failed++;
      else if (result.status === 'skipped') stats.tests.skipped++;
    }
  }

  onEnd() {
    for (const stats of this.flowStats.values()) {
      if (stats.tests.total === 0)                                          stats.status = 'missing';
      else if (stats.tests.failed > 0)                                      stats.status = 'failing';
      else if (stats.tests.passed > 0 && stats.tests.skipped === 0)        stats.status = 'covered';
      else                                                                   stats.status = 'partial';
    }
    this.printReport();
    this.writeJsonReport();
  }

  printReport() {
    const flows   = Array.from(this.flowStats.values());
    const covered = flows.filter((f) => f.status === 'covered');
    const partial = flows.filter((f) => f.status === 'partial');
    const failing = flows.filter((f) => f.status === 'failing');
    const missing = flows.filter((f) => f.status === 'missing');
    const total   = flows.length;
    const pct     = (n) => (total > 0 ? ((n / total) * 100).toFixed(1) : '0.0');

    const C = {
      reset: '\x1b[0m', bold: '\x1b[1m', dim: '\x1b[2m',
      red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m',
      brightGreen: '\x1b[92m', orange: '\x1b[38;5;208m', gray: '\x1b[90m',
    };

    console.log(`\n${C.bold}╔══════════════════════════════════════════╗${C.reset}`);
    console.log(`${C.bold}║         FLOW COVERAGE REPORT             ║${C.reset}`);
    console.log(`${C.bold}╚══════════════════════════════════════════╝${C.reset}\n`);

    console.log(`${C.bold}📊 SUMMARY${C.reset}`);
    console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
    console.log(`   Total Flows Defined:  ${C.bold}${total}${C.reset}`);
    console.log(`   ${C.green}✅ Covered:${C.reset}           ${covered.length} (${pct(covered.length)}%)`);
    console.log(`   ${C.yellow}⚠️  Partial:${C.reset}           ${partial.length} (${pct(partial.length)}%)`);
    console.log(`   ${C.red}❌ Failing:${C.reset}           ${failing.length} (${pct(failing.length)}%)`);
    console.log(`   ${C.gray}⬜ Missing:${C.reset}           ${missing.length} (${pct(missing.length)}%)\n`);

    if (missing.length > 0) {
      const p1 = missing.filter((f) => f.definition.priority === 'P1');
      const p2 = missing.filter((f) => f.definition.priority === 'P2');
      const p3 = missing.filter((f) => f.definition.priority === 'P3');

      console.log(`${C.bold}🚨 MISSING FLOWS BY PRIORITY${C.reset}`);
      console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
      if (p1.length > 0) {
        console.log(`   ${C.red}🔴 P1 (Critical): ${p1.length}${C.reset}`);
        p1.forEach((f) => console.log(`      ${C.dim}-${C.reset} ${f.flowId}: ${f.definition.name}`));
      }
      if (p2.length > 0) {
        console.log(`   ${C.orange}🟠 P2 (High): ${p2.length}${C.reset}`);
        p2.forEach((f) => console.log(`      ${C.dim}-${C.reset} ${f.flowId}: ${f.definition.name}`));
      }
      if (p3.length > 0) {
        console.log(`   ${C.yellow}🟡 P3 (Medium): ${p3.length}${C.reset}`);
        p3.forEach((f) => console.log(`      ${C.dim}-${C.reset} ${f.flowId}: ${f.definition.name}`));
      }
      console.log('');
    }

    if (failing.length > 0) {
      console.log(`${C.bold}❌ FAILING FLOWS${C.reset}`);
      console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
      for (const f of failing) {
        console.log(`   ${C.red}${f.flowId}${C.reset}: ${f.tests.failed}/${f.tests.total} failed`);
      }
      console.log('');
    }

    if (partial.length > 0) {
      console.log(`${C.bold}⚠️  PARTIAL COVERAGE${C.reset}`);
      console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
      for (const f of partial) {
        const p = f.tests.total > 0 ? ((f.tests.passed / f.tests.total) * 100).toFixed(0) : '0';
        console.log(`   ${C.yellow}${f.flowId}${C.reset}: ${p}% (${f.tests.passed}/${f.tests.total})`);
        if (f.definition.knownGaps) {
          f.definition.knownGaps.forEach((g) => console.log(`      ${C.dim}└─ Gap: ${g}${C.reset}`));
        }
      }
      console.log('');
    }

    console.log(`${C.bold}📦 COVERAGE BY MODULE${C.reset}`);
    console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
    const byModule = new Map();
    for (const flow of flows) {
      const mod = flow.definition.module;
      if (!byModule.has(mod)) byModule.set(mod, { covered: 0, total: 0 });
      byModule.get(mod).total++;
      if (flow.status === 'covered') byModule.get(mod).covered++;
    }
    for (const [mod, s] of Array.from(byModule.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
      const p = s.total > 0 ? ((s.covered / s.total) * 100).toFixed(0) : '0';
      const n = parseInt(p, 10);
      const color = n >= 80 ? C.brightGreen : n >= 60 ? C.green : n >= 40 ? C.yellow : n >= 20 ? C.orange : C.red;
      const bar = `[${'█'.repeat(Math.round((s.covered / s.total) * 20))}${'░'.repeat(20 - Math.round((s.covered / s.total) * 20))}]`;
      console.log(`   ${mod.padEnd(18)} ${color}${bar}${C.reset} ${color}${p}%${C.reset} (${s.covered}/${s.total})`);
    }
    console.log('');

    if (this.unmappedTests.length > 0) {
      console.log(`${C.bold}⚠️  TESTS WITHOUT FLOW TAG${C.reset}`);
      console.log(`${C.dim}${'─'.repeat(50)}${C.reset}`);
      console.log(`   ${this.unmappedTests.length} tests are not tagged with @flow:`);
      const grouped = new Map();
      for (const t of this.unmappedTests) grouped.set(t.file, (grouped.get(t.file) || 0) + 1);
      const sorted = Array.from(grouped.entries()).sort((a, b) => b[1] - a[1]);
      sorted.slice(0, 15).forEach(([file, count]) => {
        console.log(`      ${C.dim}${file.split('/').slice(-2).join('/')}: ${count} tests${C.reset}`);
      });
      if (sorted.length > 15) console.log(`      ${C.dim}... and ${sorted.length - 15} more${C.reset}`);
      console.log('');
    }

    console.log(`${C.dim}${'═'.repeat(50)}${C.reset}`);
    console.log(`${C.green}  ✅ JSON report: ${this.outputDir}/flow-coverage.json${C.reset}\n`);
  }

  writeJsonReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.flowStats.size,
        covered: Array.from(this.flowStats.values()).filter((f) => f.status === 'covered').length,
        partial: Array.from(this.flowStats.values()).filter((f) => f.status === 'partial').length,
        failing: Array.from(this.flowStats.values()).filter((f) => f.status === 'failing').length,
        missing: Array.from(this.flowStats.values()).filter((f) => f.status === 'missing').length,
      },
      flows: Object.fromEntries(
        Array.from(this.flowStats.entries()).map(([id, s]) => [
          id, { ...s, specs: Array.from(s.specs) },
        ])
      ),
      unmappedTests: {
        count: this.unmappedTests.length,
        files: Object.fromEntries(
          (() => { const m = new Map(); this.unmappedTests.forEach((t) => m.set(t.file, (m.get(t.file) || 0) + 1)); return m; })()
        ),
      },
    };
    if (!fs.existsSync(this.outputDir)) fs.mkdirSync(this.outputDir, { recursive: true });
    fs.writeFileSync(path.join(this.outputDir, 'flow-coverage.json'), JSON.stringify(report, null, 2));
  }
}

export default FlowCoverageReporter;
