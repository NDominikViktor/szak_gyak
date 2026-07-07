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

## TypeScript

A TypeScript a JavaScript egy szuperhalmaza, amely statikus típusrendszert
ad hozzá, és fordítás (vagy futásidejű transzpilálás) során tiszta
JavaScript-té alakul. Nem külön nyelv a JS-hez képest, hanem annak
kiterjesztése — minden érvényes JavaScript kód egyben érvényes TypeScript
kód is.

**Miért releváns a projekthez:** a [korábban vizsgált futtatókörnyezetek
közül](node-deno-bun.md) a Deno és a Bun natívan (külön build-lépés
nélkül) futtat TypeScript fájlokat, a Node.js-hez pedig `tsc` vagy
`ts-node`/`tsx` szükséges. Egy TypeScript alapú átálláshoz a fő előny a
korai hibafelismerés lenne (pl. az üzenetstruktúrák, a WebSocket
üzenettípusok vagy a titkosítási függvények paramétereinek
típusellenőrzése fordítási időben, nem futásidőben) — ez különösen
hasznos lehet egy olyan projektnél, ahol a kliens és szerver között
struktúrált üzenetek (JSON payloadok) közlekednek.

A jelenlegi fázisban a projekt sima JavaScript-ben készül, de a
TypeScript-re való átállás egy ésszerű jövőbeli lépés lehet, különösen
ha a kódbázis mérete nő.
