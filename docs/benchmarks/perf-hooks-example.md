# Teljesítmény- és memóriamérés

Cél: a titkosítási réteg (E2EE) hatásának mérése a rendszer
teljesítményére — üzenetméret és feldolgozási idő közötti összefüggés,
valamint a szerver terhelhetősége.

## 1. Titkosítási idő mérése (`perf_hooks`)

```javascript title="encrypt-benchmark.js"
const { performance } = require('node:perf_hooks');
const crypto = require('node:crypto');

async function generateKey() {
  return crypto.webcrypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  );
}

async function encrypt(key, data) {
  const iv = crypto.webcrypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.webcrypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    data
  );
  return { iv, ciphertext };
}

async function runBenchmark() {
  const key = await generateKey();
  const sizes = [100, 1_000, 10_000, 100_000, 1_000_000]; // byte-ban

  console.log('Üzenetméret (byte) | Átlagos titkosítási idő (ms)');
  console.log('--------------------------------------------------');

  for (const size of sizes) {
    const data = crypto.randomBytes(size);
    const iterations = 100;
    let total = 0;

    for (let i = 0; i < iterations; i++) {
      const start = performance.now();
      await encrypt(key, data);
      const end = performance.now();
      total += (end - start);
    }

    const avg = (total / iterations).toFixed(3);
    console.log(`${size.toString().padEnd(18)} | ${avg}`);
  }
}

runBenchmark();
```

Futtatás: `node encrypt-benchmark.js`

### Eredmény

!!! info "Frissebb, kibővített mérés"
    Ez az eredeti (első körös) mérés — a kibővített, warm-up-kiszűrt és
    mindhárom futtatókörnyezetre (Node/Deno/Bun) elvégzett verzió a
    [Node.js vs. Deno vs. Bun](../research/node-deno-bun.md) oldalon
    található.

| Üzenetméret | Átlagos titkosítási idő |
|---:|---:|
| 100 byte | 0,430 ms |
| 1 000 byte | 0,324 ms |
| 10 000 byte | 0,389 ms |
| 100 000 byte | 0,514 ms |
| 1 000 000 byte (1 MB) | 2,752 ms |

!!! note "Megfigyelés"
    Kis és közepes üzenetméreteknél (100 byte – 100 KB) a titkosítási idő
    gyakorlatilag konstans marad, mert a fix rezsi (kulcskezelés,
    API-hívás overhead) dominál. Csak 1 MB környékén válik érdemben
    mérhetővé az adatmennyiség hatása. Tipikus chat-üzeneteknél (néhány
    száz byte) a titkosítás overhead-je elhanyagolható; nagyobb
    payloadoknál (pl. fájlküldés) viszont már számít.

## 2. HTTP szerver terheléses tesztje (`autocannon`)

```javascript title="server.js"
const http = require('node:http');

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = [];
    req.on('data', (chunk) => body.push(chunk));
    req.on('end', () => {
      const payload = Buffer.concat(body);
      const decoded = payload.toString('base64');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ received: decoded.length }));
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(3000, () => console.log('Szerver fut: http://localhost:3000'));
```

Futtatás:

```bash
node server.js
```

Terheléses teszt másik terminálban:

```bash
autocannon -m POST -b '{"message":"teszt üzenet"}' -c 10 -d 10 http://localhost:3000
```

10 párhuzamos kapcsolattal, 10 másodpercig teszteli a szervert.

### Eredmény (két egymást követő futtatás)

| Futtatás | Átlagos req/mp | Átlagos latency | p97.5 latency |
|---|---:|---:|---:|
| 1. kör | 5 221,9 | 1,43 ms | 5 ms |
| 2. kör | 6 787,2 | 0,95 ms | 3 ms |

!!! note "Megfigyelés"
    A második futtatás jobb teljesítményt mutatott, valószínűleg a
    Node.js V8 motorjának JIT-bemelegedése miatt (a gyakran futó
    kódrészek az első futás után natív gépi kódra fordulnak). Ez azt is
    jelenti, hogy egyetlen mérés önmagában megtévesztő lehet — a
    megbízható benchmarkoláshoz több egymást követő futtatás és az
    eredmények átlagolása szükséges.

## Következő lépés (opcionális)

A `clinic.js` eszközkészlettel (`clinic doctor -- node server.js`) vizuális
flame graph és event loop delay riport is készíthető, ami mélyebb
betekintést ad a CPU-terhelés eloszlásába. Ez a jelen fázisban opcionális
kiegészítés, a fő mérési eredmények (fenti két táblázat) már megvannak.
