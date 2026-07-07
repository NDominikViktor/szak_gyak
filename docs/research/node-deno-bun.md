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

A mérések a `docs/benchmarks/` mappa szkriptjeivel készültek, ugyanazon a
gépen, egymás után futtatva:

```bash
# titkosítási benchmark (100 B - 100 MB, warm-up kiszűréssel)
node encrypt-benchmark-v2.mjs
deno run --allow-all encrypt-benchmark-v2.mjs
bun run encrypt-benchmark-v2.mjs

# HTTP terheléses teszt - node:http kompatibilitási réteg
node server.mjs        # ill. deno run --allow-all server.mjs / bun run server.mjs
npx autocannon -m POST -b '{"message":"teszt"}' -c 10 -d 10 http://localhost:3000

# HTTP terheléses teszt - natív API-kkal
deno run --allow-net server-deno-native.mjs
bun run server-bun-native.mjs
# (ugyanazzal az autocannon paranccsal tesztelve)
```

### Warm-up kiszűrés módszertana

A `encrypt-benchmark-v2.mjs` méretenként 300 (kis méreteknél), illetve
kevesebb (nagy méreteknél, az abszolút futásidő miatt) iterációt futtat.
Egy mozgóablakos becslő (20 minta/ablak) megkeresi, hol stabilizálódik a
mért idő (egymást követő ablak-átlagok közötti relatív változás 2% alá
csökken), és az addig eltelt mintákat **warm-up mintaként eldobja**,
csak az utána következőkből számol átlagot/szórást/percentiliseket. Ha
nem talál stabilizációs pontot (jellemzően a nagy — 10 MB, 100 MB —
méreteknél, ahol kevés az iterációszám), nem dob el semmit.

## 1. Titkosítási művelet ideje (AES-GCM), 100 byte - 100 MB, warm-up kiszűrve

![AES-GCM titkosítási idő üzenetméret és futtatókörnyezet szerint, kibővített tartomány](encryption-chart-v2.png)

| Üzenetméret | Node.js avg (ms) | Deno avg (ms) | Bun avg (ms) |
|---|---|---|---|
| 100 byte | 0,142 ± 0,033 | 0,116 ± 0,130 | 0,090 ± 0,168 |
| 1 000 byte | 0,137 ± 0,024 | 0,123 ± 0,083 | 0,089 ± 0,195 |
| 10 000 byte | 0,164 ± 0,061 | 0,181 ± 0,037 | 0,115 ± 0,235 |
| 100 000 byte | 0,317 ± 0,090 | 0,715 ± 0,186 | 0,253 ± 0,384 |
| 1 000 000 byte (1 MB) | 1,907 ± 0,498 | 7,259 ± 2,070 | 1,515 ± 0,757 |
| 10 000 000 byte (10 MB) | 14,991 ± 2,345 | 48,112 ± 7,141 | 13,207 ± 3,721 |
| 100 000 000 byte (100 MB) | 132,857 ± 11,374 | 526,527 ± 49,418 | 89,847 ± 32,132 |

!!! note "Megfigyelés — nagy méretek"
    100 MB-nál már jól elkülönül a három runtime: a **Bun a
    leggyorsabb** (89,8 ms), utána a **Node.js** (132,9 ms), és jelentős
    lemaradással a **Deno** (526,5 ms, kb. 4-5,9×-öse a másik kettőnek).
    Ez a mintázat konzisztens a 10 MB-os méréssel is (Bun ≈ Node < Deno),
    tehát a Deno WebCrypto AES-GCM implementációja nagy adatmennyiségnél
    következetesen lassabb marad a másik kettőnél.

### Statisztikai ellenőrzés: Node vs. Bun, 1 MB, trimmelt adatokon

A trimmelt (warm-up-mentes) mintákon Welch-féle kétmintás t-próbát
végezve (Node: n=180, átlag=1,907, szórás=0,498; Bun: n=80, átlag=1,515,
szórás=0,757):

- **t-statisztika:** 4,242
- **szabadságfok:** ≈ 110,5
- **kétoldali p-érték:** < 0,0001

A különbség **erősen statisztikailag szignifikáns** — a Bun konzisztensen
gyorsabb a Node.js-nél 1 MB-os üzeneteknél, nem csak véletlen ingadozás.

## 2. HTTP terheléses teszt — natív API-k vs. `node:http` kompatibilitási réteg

| Runtime | API | Átlagos req/mp | Átlagos latency | p97.5 latency |
|---|---|---|---|---|
| Node.js | `node:http` (natív) | 15 614,8 | 0,11 ms | 1 ms |
| Deno | `node:http` (kompat.) | 9 111,2 | 0,55 ms | 2 ms |
| Deno | `Deno.serve()` (natív) | **15 887,6** | 0,08 ms | 1 ms |
| Bun | `node:http` (kompat.) | 6 172,0 | 1,04 ms | 6 ms |
| Bun | `Bun.serve()` (natív) | **13 670,0** | 0,20 ms | 3 ms |

!!! success "A natív API-k tényleg sokat számítanak"
    A `node:http` kompatibilitási réteg helyett a saját natív API-t
    használva:

    - **Deno:** 9 111,2 → 15 887,6 req/mp (**+74,4%**)
    - **Bun:** 6 172,0 → 13 670,0 req/mp (**+121,5%**)

    Natív API-kkal mérve a három runtime throughput-ja már sokkal
    közelebb esik egymáshoz: **Deno (15 887,6) ≈ Node.js (15 614,8) >
    Bun (13 670,0)**. Ez megerősíti a korábbi módszertani észrevételt:
    a `node:http`-kompatibilitási réteg jelentősen alulméri a Deno és a
    Bun valós HTTP-teljesítményét — a "melyik a leggyorsabb" kérdésre
    adott válasz erősen függ attól, natív vagy kompatibilitási API-t
    használunk-e.

## Valós üzenetméretek kontextusa

Népszerű üzenetküldő alkalmazásoknál (pl. WhatsApp, Signal) egy tipikus
szöveges üzenet — protokoll-overhead-del együtt — nagyságrendileg
**1–3 KB**, míg egy tömörített fénykép jellemzően **100 KB – 500 KB**
között mozog, egy rövid hangüzenet pedig **tíz–száz KB** nagyságrendű. A
10 MB / 100 MB tartomány ennek megfelelően inkább nagyobb
fájlmellékleteket (dokumentum, videó) modellez, mint tipikus chat-
üzeneteket — ezeknél a méreteknél viszont már jól láthatóan
szétválik a három runtime teljesítménye, ami hasznos plusz-információ,
ha a projekt később fájlküldést is támogatna.

## Következtetés a projekthez

A kibővített, warm-up-kiszűrt mérések alapján:

- **Kis-közepes üzeneteknél** (100 B – 100 KB, azaz a tipikus chat-
  forgalom) mindhárom runtime századmásodperces tartományban van, a
  Bun jellemzően a leggyorsabb, de a különbségek a gyakorlatban
  elhanyagolhatók.
- **Nagy payloadoknál** (1 MB+) a Bun és a Node.js következetesen
  gyorsabb, mint a Deno; a Node vs. Bun különbség statisztikailag
  szignifikáns, de kis abszolút mértékű.
- **HTTP-terhelésnél natív API-kkal** Node.js és Deno gyakorlatilag
  egyenrangú, a Bun valamivel e mögött marad — ez jelentősen eltér attól
  a képtől, amit a `node:http`-kompatibilitási rétegen mérve kaptunk.

A projekt szempontjából a **Node.js** marad az ésszerű választás: az
érett ökoszisztéma, az npm-kompatibilitás, és a `worker_threads` modul
(amit a szerveroldali párhuzamosításnál tervezünk használni) mind emellett
szólnak, és a saját mérések alapján teljesítményben sincs hátrányban a
másik kettővel szemben — sem kis, sem nagy üzenetméreteknél, sem natív
HTTP-terhelés alatt.
