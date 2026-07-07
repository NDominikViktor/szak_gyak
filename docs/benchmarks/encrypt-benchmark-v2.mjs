// encrypt-benchmark-v2.mjs
// v2: nagyobb méretek (10 MB, 100 MB) + JIT warm-up kiszűrés
// Fut: node / deno run --allow-all / bun run encrypt-benchmark-v2.mjs
import { performance } from 'node:perf_hooks';
import crypto from 'node:crypto';

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

  return { raw: stats(samples), trimmed: stats(trimmed), cutoff };
}

async function runBenchmark() {
  const key = await generateKey();
  // kis/közepes méretek kevesebb iterációval (mint eddig), a nagyok
  // kevesebb iterációval, mert azok abszolút ideje már nagyobb
  const plan = [
    { size: 100, iterations: 300 },
    { size: 1_000, iterations: 300 },
    { size: 10_000, iterations: 300 },
    { size: 100_000, iterations: 300 },
    { size: 1_000_000, iterations: 200 },
    { size: 10_000_000, iterations: 50 },
    { size: 100_000_000, iterations: 15 },
  ];

  console.log(`Runtime: ${detectRuntime()}`);
  console.log(
    'size(byte) | n | warmup_cutoff | raw_avg(ms) | trimmed_avg(ms) | trimmed_stddev | trimmed_p50 | trimmed_p95'
  );
  console.log('-'.repeat(110));

  for (const { size, iterations } of plan) {
    const { raw, trimmed, cutoff } = await runSize(key, size, iterations);
    console.log(
      `${size.toString().padEnd(11)} | ${String(iterations).padEnd(3)} | ${String(cutoff).padEnd(13)} | ${raw.avg.padEnd(11)} | ${trimmed.avg.padEnd(16)} | ${trimmed.stddev.padEnd(14)} | ${trimmed.p50.padEnd(11)} | ${trimmed.p95}`
    );
  }
}

function detectRuntime() {
  if (typeof Deno !== 'undefined') return `Deno ${Deno.version.deno}`;
  if (typeof Bun !== 'undefined') return `Bun ${Bun.version}`;
  return `Node.js ${process.version}`;
}

runBenchmark();
