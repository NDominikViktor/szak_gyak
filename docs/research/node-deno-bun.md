# Node.js vs. Deno vs. Bun — saját mérések

## Áttekintés

A három JavaScript futtatókörnyezet közül a **Node.js** a legrégebbi és
legérettebb, hatalmas npm ökoszisztémával. A **Deno** (ugyanattól a
fejlesztőtől, Ryan Dahl-tól, aki a Node.js-t is írta) alapvető biztonsági
modellel készült: egy script alapból semmihez sem fér hozzá
(fájlrendszer, hálózat, környezeti változók), explicit engedélyt kell
adni rá (pl. `--allow-net`), emellett natívan támogatja a TypeScript-et.
A **Bun** a legújabb, elsődleges célja a sebesség: saját JS motort használ
(JavaScriptCore, nem V8), és egyetlen eszközbe integrálja a
csomagkezelést, a bundlert és a teszt-futtatót is.

## Mérési környezet

| | |
|---|---|
| **CPU** | 12th Gen Intel(R) Core(TM) i5-1235U (12 mag/szál) |
| **RAM** | 16,9 GB |
| **OS** | Windows 11 23H2 (build 22631) |
| **Node.js verzió** | v20.10.0 |
| **Deno verzió** | 2.9.1 |
| **Bun verzió** | 1.3.14 |

## Reprodukálhatóság

A mérések a `docs/benchmarks/encrypt-benchmark.mjs` és
`docs/benchmarks/server.mjs` szkriptekkel készültek, ugyanazon a gépen,
egymás után futtatva:

```bash
# titkosítási benchmark, futtatókörnyezetenként
node encrypt-benchmark.mjs
deno run --allow-all encrypt-benchmark.mjs
bun run encrypt-benchmark.mjs

# HTTP terheléses teszt (a szervert külön terminálban indítva,
# majd autocannon-nal terhelve 10 párhuzamos kapcsolattal, 10 mp-ig)
node server.mjs        # ill. deno run --allow-all server.mjs / bun run server.mjs
npx autocannon -m POST -b '{"message":"teszt"}' -c 10 -d 10 http://localhost:3000
```

A titkosítási szkript minden üzenetméretnél 100 iterációt futtat, és a
kapott mintákból számolja az átlagot, szórást, minimumot, maximumot,
valamint a p50/p95 percentiliseket.

## 1. Titkosítási művelet ideje (AES-GCM)

![AES-GCM titkosítási idő üzenetméret és futtatókörnyezet szerint](encryption-chart.png)

### 100 byte

| Runtime | Átlag (ms) | Szórás | Min | Max | p50 | p95 |
|---|---|---|---|---|---|---|
| Node.js | 0,199 | 0,109 | 0,034 | 0,860 | 0,184 | 0,382 |
| Deno | 0,247 | 0,479 | 0,023 | 4,916 | 0,196 | 0,382 |
| Bun | 0,087 | 0,352 | 0,007 | 3,558 | 0,043 | 0,153 |

### 1 000 byte

| Runtime | Átlag (ms) | Szórás | Min | Max | p50 | p95 |
|---|---|---|---|---|---|---|
| Node.js | 0,075 | 0,057 | 0,034 | 0,373 | 0,039 | 0,174 |
| Deno | 0,161 | 0,062 | 0,042 | 0,281 | 0,181 | 0,247 |
| Bun | 0,074 | 0,038 | 0,013 | 0,219 | 0,064 | 0,153 |

### 10 000 byte

| Runtime | Átlag (ms) | Szórás | Min | Max | p50 | p95 |
|---|---|---|---|---|---|---|
| Node.js | 0,049 | 0,031 | 0,036 | 0,204 | 0,039 | 0,117 |
| Deno | 0,196 | 0,070 | 0,084 | 0,498 | 0,190 | 0,310 |
| Bun | 0,117 | 0,300 | 0,045 | 3,092 | 0,081 | 0,148 |

### 100 000 byte

| Runtime | Átlag (ms) | Szórás | Min | Max | p50 | p95 |
|---|---|---|---|---|---|---|
| Node.js | 0,166 | 0,092 | 0,081 | 0,518 | 0,162 | 0,329 |
| Deno | 0,578 | 0,126 | 0,327 | 0,845 | 0,633 | 0,734 |
| Bun | 0,230 | 0,433 | 0,070 | 3,638 | 0,159 | 0,414 |

### 1 000 000 byte (1 MB)

| Runtime | Átlag (ms) | Szórás | Min | Max | p50 | p95 |
|---|---|---|---|---|---|---|
| Node.js | 1,003 | 0,466 | 0,441 | 3,525 | 0,861 | 1,990 |
| Deno | 4,737 | 0,804 | 3,783 | 7,212 | 4,365 | 6,303 |
| Bun | 0,802 | 0,491 | 0,469 | 3,212 | 0,687 | 1,926 |

!!! note "Megfigyelés"
    1 MB-os üzeneteknél a Deno kb. 4,7×-ese lassabb, mint a Node.js vagy a
    Bun. Kisebb (100 byte – 10 KB) üzeneteknél a Bun konzisztensen a
    leggyorsabb vagy a Node.jshoz hasonló, a Deno viszont már itt is
    lassabb. A szórás minden runtime-nál jelentős a kis méreteknél — ez
    a JIT-bemelegedés és a mérési zaj hatását mutatja, amit egy
    finomabb módszertannal (lásd alább) csökkenteni lehetne.

### Statisztikai ellenőrzés: valóban "gyakorlatilag azonos" a Node és a Bun 1 MB-nál?

Az összegző statisztikák (átlag, szórás, n=100) alapján egy Welch-féle
kétmintás t-próbát végeztünk a Node.js és a Bun 1 MB-os eredményein:

- **t-statisztika:** 2,969
- **szabadságfok:** ≈ 197,5
- **közelítő kétoldali p-érték:** ≈ 0,003

**Ez azt jelenti, hogy a különbség statisztikailag szignifikáns**
(p < 0,05), annak ellenére, hogy a nyers számérték (0,201 ms) kicsinek
tűnik. A korábbi "gyakorlatilag azonos" megfogalmazás pontatlan volt —
helyesen úgy fogalmazható meg, hogy **a különbség abszolút értékben kicsi,
de statisztikailag kimutatható**, tehát a Bun konzisztensen (ha csak kis
mértékben is) gyorsabb, mint a Node.js 1 MB-os üzeneteknél.

!!! warning "Módszertani korlát"
    Ez a t-próba az összegző statisztikákból (átlag, szórás) lett
    visszaszámolva, nem a nyers mintákból — ez normáleloszlást
    feltételez, amit a megfigyelt nagy max-értékek (kiugró, valószínűleg
    JIT-hatásból eredő minták) valójában megkérdőjeleznek. Egy pontosabb
    elemzéshez a nyers idősorokat kellene megőrizni és azon nem-paraméteres
    próbát (pl. Mann-Whitney U) futtatni.

## 2. HTTP terheléses teszt (`autocannon`, 10 párhuzamos kapcsolat, 10 mp)

| Runtime | Átlagos req/mp | Átlagos latency | p97.5 latency | Összes kérés (10 mp alatt) |
|---|---|---|---|---|
| Node.js | 15 614,8 | 0,11 ms | 1 ms | 156 000 |
| Deno | 9 111,2 | 0,55 ms | 2 ms | 91 000 |
| Bun | 6 172,0 | 1,04 ms | 6 ms | 62 000 |

!!! warning "Fontos korlátozás"
    Ez az eredmény **nem** a Bun általánosan hangoztatott nyers
    sebességi előnyét tükrözi. A teszt szándékosan a Node.js beépített
    `node:http` API-ját használta mindhárom runtime-on (kompatibilitási
    rétegen keresztül Deno-ban és Bun-ban), hogy a kód azonos legyen. A
    Bun saját, natív `Bun.serve()` API-ja és a Deno saját `Deno.serve()`
    API-ja ennél lényegesen jobb throughput-ot szokott adni — ez a mérés
    tehát a Node.js-kompatibilitási réteg teljesítményét méri, nem a
    natív implementációkét. **Következő lépésként érdemes lenne
    `Deno.serve()` és `Bun.serve()` alapú szervert is megírni és
    lemérni**, hogy a natív API-k tényleges előnye is látszódjon.

## Valós üzenetméretek kontextusa

Népszerű üzenetküldő alkalmazásoknál (pl. WhatsApp, Signal) egy tipikus
szöveges üzenet — protokoll-overhead-del együtt — nagyságrendileg
**1–3 KB**, míg egy tömörített fénykép jellemzően **100 KB – 500 KB**
között mozog, egy rövid hangüzenet pedig **tíz–száz KB** nagyságrendű. A
mi tesztelt tartományunk (100 byte – 1 MB) ezt jól lefedi: a kis
üzenetméretek (100 byte – 10 KB) a valós szöveges chat-üzenetekhez
hasonlítanak, míg az 1 MB inkább egy csatolt kép/rövid hangüzenet
nagyságrendjét közelíti.

## További vizsgálandó irányok (jövőbeli munka)

- **10 MB / 100 MB méretű üzenetek mérése** — nagyobb fájlküldés (pl.
  videó, dokumentum) szcenáriójának lefedésére
- **JIT-bemelegedés kiszűrése** — nagyobb mintaszám mellett az első
  néhány száz mérés eldobása, és annak kimérése/becslése, hány mintát
  érdemes kihagyni a stabil állapot eléréséhez
- **`Deno.serve()` és `Bun.serve()` natív mérése** a jelenlegi
  `node:http`-kompatibilitási réteg helyett

## Következtetés a projekthez

A saját mérések alapján a **Node.js** maradt a legjobb,
legkiegyensúlyozottabb választás ezen a gépen: titkosításnál kis és
közepes üzenetméreteknél versenyképes, 1 MB-nál statisztikailag kimutathatóan
(bár kis mértékben) lassabb a Bun-nál; HTTP-terhelésnél pedig a
`node:http` kompatibilitási rétegen keresztül mérve ez volt a
leggyorsabb.

A projekt szempontjából emellett továbbra is a Node.js mellett szól az
érett ökoszisztéma, az npm-kompatibilitás, és a `worker_threads` modul,
amit a szerveroldali párhuzamosításnál tervezünk használni.
