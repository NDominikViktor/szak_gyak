# JavaScript nyelv és ECMAScript szabványok

Az áttekintés alapja az [MDN JavaScript
Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide), a
verziótörténethez pedig a [TC39 proposals
repó](https://github.com/tc39/proposals).

## A legfontosabb ECMAScript mérföldkövek

- **ES5 (2009)** — a "régi" JavaScript: `var`, prototípus-alapú öröklés
- **ES6 / ES2015** — nagy váltás: `let`/`const`, arrow function,
  `class` szintaxis, `Promise`, template literal, modulok
  (`import`/`export`), destructuring
- **ES2017** — `async`/`await` — ez különösen fontos a projekthez, mert a
  Node.js aszinkron I/O-modellje erre épül
- **ES2020** — optional chaining (`?.`), nullish coalescing (`??`)
- **ES2021+** — kisebb, kényelmi kiegészítések (pl. `Array.prototype.at()`,
  top-level `await`)

## A projekthez különösen releváns részek

- **`async`/`await` és `Promise`** — a kliens-szerver kommunikáció (HTTP
  kérések, WebSocket üzenetváltás) gerince
- **`Map` / `Set`** — hasznos lehet pl. aktív kapcsolatok vagy
  üzenetsorok kezelésére a szerveroldalon
- **Modulok (`import`/`export`)** — a tiszta, moduláris kódstruktúra
  kialakításához, ami a projekt egyik célkitűzése volt
