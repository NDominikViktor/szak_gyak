// encrypt-benchmark-v2.mjs
// v2: nagyobb méretek (10 MB, 100 MB) + JIT warm-up kiszűrés
//
// Fut: node / deno run --allow-all / bun run encrypt-benchmark-v2.mjs [opciók]
//
// Opciók (mindegyik elhagyható):
//   --csv=<útvonal>            összesített statisztikák (n, avg, stddev,
//                               p50, p95, cutoff) hozzáfűzése egy CSV-hez -
//                               ebből generálja a diagramokat a
//                               generate_charts.py szkript.
//   --raw-samples=<útvonal>    minden egyes mért minta (nyers, méretenkénti
//                               idősor) elmentése - ez kell a warm-up
//                               algoritmus valós adaton történő
//                               szemléltetéséhez.
//   --iteration-multiplier=N   az alap iterációszámok N-szerese (pl. 5 =
//                               ötszörös iterációszám a nagyobb mintavétel
//                               vizsgálatához, ld. worklog).
import { performance } from 'node:perf_hooks';
import crypto from 'node:crypto';
import { appendFileSync, existsSync, writeFileSync } from 'node:fs';

async function generateKey() {
  return crypto.webcrypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  );
}

async function encrypt(key, data) {
  const iv = crypto.webcrypto.getRandomValues(new Uint8Array(12));
  return crypto.webcrypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, data);
}

function stats(samples) {
  const sorted = [...samples].sort((a, b) => a - b);
  const n = sorted.length;
  const avg = samples.reduce((a, b) => a + b, 0) / n;
  const variance = samples.reduce((a, b) => a + (b - avg) ** 2, 0) / n;
  const stddev = Math.sqrt(variance);
  return {
    n,
    avg: avg.toFixed(3),
    stddev: stddev.toFixed(3),
    min: sorted[0].toFixed(3),
    max: sorted[n - 1].toFixed(3),
    p50: sorted[Math.floor(n * 0.5)].toFixed(3),
    p95: sorted[Math.floor(n * 0.95)].toFixed(3),
  };
}

// Megbecsüli, hány kezdő mintát érdemes eldobni: addig nézi a mozgó
// átlagot 20-as ablakban, amíg az egymást követő ablak-átlagok közötti
// relatív változás egy küszöb (2%) alá nem esik, és ez stabilan is marad.
function estimateWarmupCutoff(samples, windowSize = 20, threshold = 0.02) {
  if (samples.length < windowSize * 3) return 0;
  const windowAvgs = [];
  for (let i = 0; i + windowSize <= samples.length; i += windowSize) {
    const window = samples.slice(i, i + windowSize);
    windowAvgs.push(window.reduce((a, b) => a + b, 0) / windowSize);
  }
  for (let i = 1; i < windowAvgs.length - 1; i++) {
    const change = Math.abs(windowAvgs[i] - windowAvgs[i - 1]) / windowAvgs[i - 1];
    if (change < threshold) {
      return i * windowSize;
    }
  }
  return Math.floor(samples.length * 0.1); // fallback: első 10% eldobása
}

async function runSize(key, size, iterations) {
  const data = crypto.randomBytes(size);
  const samples = [];

  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    await encrypt(key, data);
    samples.push(performance.now() - start);
  }

  const cutoff = estimateWarmupCutoff(samples);
  const trimmed = samples.slice(cutoff);

  return { raw: stats(samples), trimmed: stats(trimmed), cutoff, samples };
}

// Méret -> iterációszám leképezés. A kis/közepes méreteknél (<=1e5 byte)
// az abszolút futásidő elhanyagolható, ezért egységesen 300 iteráció fut
// (elég minta a warm-up-becsléshez, ld. lentebb). 1e6 byte fölött az
// abszolút idő már számottevő (ld. docs/research/node-deno-bun.md, 1.
// ábra), ezért az iterációszám ott a mérési idő korlátozása miatt csökken.
// A pontos küszöbök és iterációszámok dokumentálva vannak a
// "Warm-up kiszűrés módszertana" szakaszban (node-deno-bun.md).
function iterationsFor(size) {
  if (size <= 1e5) return 300; // 100 B .. 100 000 B
  if (size <= 1e6) return 200; // 1 000 000 B
  if (size <= 1e7) return 50; // 10 000 000 B
  return 15; // 100 000 000 B
}

function parseArgs() {
  const args = process.argv.slice(2);
  const get = (flag) => {
    const arg = args.find((a) => a.startsWith(`${flag}=`));
    return arg ? arg.slice(flag.length + 1) : undefined;
  };
  return {
    csvPath: get('--csv'),
    rawSamplesPath: get('--raw-samples'),
    iterationMultiplier: Number(get('--iteration-multiplier') ?? 1),
  };
}

function ensureCsvHeader(path, header) {
  if (!existsSync(path)) writeFileSync(path, header + '\n');
}

async function runBenchmark() {
  const { csvPath, rawSamplesPath, iterationMultiplier } = parseArgs();
  const key = await generateKey();
  const sizes = [1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8];
  const plan = sizes.map((size) => ({
    size,
    iterations: Math.round(iterationsFor(size) * iterationMultiplier),
  }));
  const runtime = detectRuntime();

  if (csvPath) {
    ensureCsvHeader(
      csvPath,
      'runtime,size_bytes,n,cutoff,raw_avg_ms,trimmed_avg_ms,trimmed_stddev_ms,trimmed_p50_ms,trimmed_p95_ms'
    );
  }
  if (rawSamplesPath) {
    ensureCsvHeader(rawSamplesPath, 'runtime,size_bytes,sample_index,time_ms');
  }

  console.log(`Runtime: ${runtime}`);
  console.log(
    'size(byte) | n | warmup_cutoff | raw_avg(ms) | trimmed_avg(ms) | trimmed_stddev | trimmed_p50 | trimmed_p95'
  );
  console.log('-'.repeat(110));

  for (const { size, iterations } of plan) {
    const { raw, trimmed, cutoff, samples } = await runSize(key, size, iterations);
    console.log(
      `${size.toString().padEnd(11)} | ${String(iterations).padEnd(3)} | ${String(cutoff).padEnd(13)} | ${raw.avg.padEnd(11)} | ${trimmed.avg.padEnd(16)} | ${trimmed.stddev.padEnd(14)} | ${trimmed.p50.padEnd(11)} | ${trimmed.p95}`
    );

    if (csvPath) {
      appendFileSync(
        csvPath,
        `${runtime},${size},${trimmed.n},${cutoff},${raw.avg},${trimmed.avg},${trimmed.stddev},${trimmed.p50},${trimmed.p95}\n`
      );
    }
    if (rawSamplesPath) {
      const lines = samples.map((t, i) => `${runtime},${size},${i},${t.toFixed(4)}`).join('\n');
      appendFileSync(rawSamplesPath, lines + '\n');
    }
  }
}

function detectRuntime() {
  if (typeof Deno !== 'undefined') return `Deno ${Deno.version.deno}`;
  if (typeof Bun !== 'undefined') return `Bun ${Bun.version}`;
  return `Node.js ${process.version}`;
}

runBenchmark();
