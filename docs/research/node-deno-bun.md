# Node.js vs. Deno vs. Bun

A három JavaScript futtatókörnyezet közül a **Node.js** a legrégebbi és
legérettebb, hatalmas npm ökoszisztémával, de a legrégebbi
architektúrájú is.

A **Deno** — ugyanattól a fejlesztőtől (Ryan Dahl), aki a Node.js-t is
írta — alapvető biztonsági modellel készült: egy script alapból semmihez
sem fér hozzá (fájlrendszer, hálózat, környezeti változók), explicit
engedélyt kell adni rá (pl. `--allow-net`). Emellett natívan támogatja a
TypeScript-et, külön build-lépés nélkül.

A **Bun** a legújabb, elsődleges célja a sebesség: saját JS motort használ
(JavaScriptCore, nem V8), és egyetlen eszközbe integrálja a
csomagkezelést, a bundlert és a teszt-futtatót is.

## Benchmark-eredmények (2 különböző forrás összevetése)

Két 2026-os benchmark-forrás (DevToolReviews, DEV Community) alapján a
tendencia konzisztens, de a konkrét számok jelentősen eltérnek:

- **Szintetikus terhelésen** (pl. "Hello world" JSON válasz) a Bun
  jelentősen — kb. 2×-esen — gyorsabb throughput-ot ér el, mint a Node.js,
  a Deno a kettő között helyezkedik el.
- **Valós alkalmazáshoz közelebb álló teszten** (adatbázis-hívások,
  autentikáció, komplexebb keretrendszer) a különbség jelentősen csökken,
  mert ilyenkor az I/O-várakozás dominál, nem a nyers JS-végrehajtás
  sebessége.

A konkrét számok forrásonként eltérnek (más hardver, más terhelési
profil, más mért funkcionalitás), ezért ezeket nem érdemes 1:1
összehasonlítani — az **irány** viszont mindkét forrásban ugyanaz.

## Amiben mindkét forrás egyetért

- a Bun a leggyorsabb induláskor és nyers throughput-ban, a csomagkezelője
  (`bun install`) is jelentősen gyorsabb az npm-nél
- a Deno biztonsági modellje (explicit engedélyek) egyedülálló a háromból
- a Node.js npm-kompatibilitása a legjobb, mert az egész ökoszisztéma erre
  épült
- a Node.js a legérettebb produkciós használatra

## Választás a projekthez

A projekt **Node.js** marad: az ökoszisztéma érettsége, az
npm-kompatibilitás, és a `worker_threads` modul (amit a
teljesítménymérési feladatnál direkt használunk) mind Node-specifikus,
jól dokumentált eszközök.

Emellett tanulságos megfigyelés a benchmark-mérésnél, hogy az eredmény
erősen függ attól, hogy szintetikus vagy valós terhelést mérünk — ez a
saját méréseinknél is releváns szempont (lásd
[Benchmark](../benchmarks/perf-hooks-example.md)).
