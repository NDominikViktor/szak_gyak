// run-pipeline.mjs
//
// Egy lépésben futtatja: benchmark mérés (minden elérhető runtime-on) ->
// eredmények CSV-be gyűjtése -> chartok (matplotlib) legenerálása -> MkDocs
// build. Node.js-ben fut, ezért ugyanúgy hívható, mint a benchmark
// szkriptek - nincs bash/PowerShell-függőség.
//
// Használat (a repó gyökeréből):
//   node scripts/run-pipeline.mjs
//   node scripts/run-pipeline.mjs --big     # --iteration-multiplier=5
//
// Előfeltétel: node (és, ha telepítve vannak, deno / bun) a PATH-on;
// Python + a requirements.txt csomagjai (`pip install -r requirements.txt`).

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const RESULTS_DIR = join(ROOT, 'docs', 'benchmarks', 'results');
const multiplier = process.argv.includes('--big') ? '5' : '1';

if (multiplier === '5') console.log(`Nagyobb iterációszám mód: --iteration-multiplier=${multiplier}`);

mkdirSync(RESULTS_DIR, { recursive: true });
for (const f of ['latest-run.csv', 'latest-run-raw-samples.csv', 'latest-run-pow2.csv', 'latest-run-pow2-raw-samples.csv']) {
  rmSync(join(RESULTS_DIR, f), { force: true });
}

function commandExists(cmd) {
  const probe = process.platform === 'win32' ? spawnSync('where', [cmd]) : spawnSync('which', [cmd]);
  return probe.status === 0;
}

function run(cmd, args, label) {
  if (!commandExists(cmd)) {
    console.log(`==> Kihagyva (nincs telepítve): ${label}`);
    return;
  }
  console.log(`==> Mérés futtatása: ${label}`);
  const result = spawnSync(cmd, args, { cwd: ROOT, stdio: 'inherit', shell: process.platform === 'win32' });
  if (result.status !== 0) {
    console.error(`Hiba (${label}), a mérés kimaradt, de a pipeline folytatódik.`);
  }
}

const csv = join(RESULTS_DIR, 'latest-run.csv');
const raw = join(RESULTS_DIR, 'latest-run-raw-samples.csv');
const csvPow2 = join(RESULTS_DIR, 'latest-run-pow2.csv');
const rawPow2 = join(RESULTS_DIR, 'latest-run-pow2-raw-samples.csv');

const decimalArgs = (extra) => ['docs/benchmarks/encrypt-benchmark-v2.mjs', `--csv=${csv}`, `--raw-samples=${raw}`, `--iteration-multiplier=${multiplier}`, ...extra];
const pow2Args = (extra) => ['docs/benchmarks/encrypt-benchmark-v3-pow2.mjs', `--csv=${csvPow2}`, `--raw-samples=${rawPow2}`, `--iteration-multiplier=${multiplier}`, ...extra];

run('node', decimalArgs([]), 'Node.js (decimális méretek)');
run('deno', ['run', '--allow-all', ...decimalArgs([])], 'Deno (decimális méretek)');
run('bun', ['run', ...decimalArgs([])], 'Bun (decimális méretek)');

run('node', pow2Args([]), 'Node.js (2-hatvány méretek)');
run('deno', ['run', '--allow-all', ...pow2Args([])], 'Deno (2-hatvány méretek)');
run('bun', ['run', ...pow2Args([])], 'Bun (2-hatvány méretek)');

console.log('==> Chartok generálása');
let py = spawnSync('python', ['docs/benchmarks/generate_charts.py'], { cwd: ROOT, stdio: 'inherit' });
if (py.status !== 0) spawnSync('python3', ['docs/benchmarks/generate_charts.py'], { cwd: ROOT, stdio: 'inherit' });

console.log('==> MkDocs build');
spawnSync('python', ['-m', 'mkdocs', 'build'], { cwd: ROOT, stdio: 'inherit' });

console.log(`==> Kész. Eredmények: ${csv}, ${raw}`);
console.log('    Ábrák frissítve: docs/benchmarks/*.png, docs/*.png, docs/research/*.png');
