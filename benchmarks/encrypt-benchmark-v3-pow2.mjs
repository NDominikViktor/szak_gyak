// encrypt-benchmark-v3-pow2.mjs
// v3: kettes-hatvány alapú méretek (KiB/MiB pontos többszörösei) - a
// decimális (v2) méréssorozat finomított, precízebb változata.
//
// Fut: node / deno run --allow-all / bun run encrypt-benchmark-v3-pow2.mjs [opciók]
//
// Opciók (mindegyik elhagyható), megegyeznek a v2 szkriptével:
//   --csv=<útvonal>            összesített statisztikák CSV-be fűzése
//   --raw-samples=<útvonal>    nyers minták elmentése (warm-up szemléltetéshez)
//   --iteration-multiplier=N   iterációszám N-szerese
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

// Méret (byte) -> iterációszám, ugyanazzal a küszöb-logikával, mint a
// decimális (v2) szkriptben - ld. ott a részletes indoklást.
function iterationsFor(size) {
  if (size <= 2 ** 16) return 300; // 128 B .. 64 KiB
  if (size <= 2 ** 20) return 200; // 1 MiB
  if (size <= 2 ** 23) return 50; // 8 MiB
  return 15; // 64 MiB
}

async function runBenchmark() {
  const { csvPath, rawSamplesPath, iterationMultiplier } = parseArgs();
  const key = await generateKey();
  // Kettes-hatvány alapú méretek (KiB/MiB pontos többszörösei), a
  // decimális (v2) méréssorozat finomított, precízebb változata.
  const sizes = [2 ** 7, 2 ** 10, 2 ** 13, 2 ** 16, 2 ** 20, 2 ** 23, 2 ** 26];
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
