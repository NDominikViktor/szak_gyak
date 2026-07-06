# JavaScript Runtime Comparison: Node.js, Deno, Bun

## 1. Architektonikus áttekintés

A modern JavaScript futtatókörnyezetek értékelése során az alábbi technikai szempontokat vizsgáltuk az E2EE (End-to-End Encryption) chat-alkalmazás implementációjához:

| Szempont | Node.js | Deno | Bun |
| :--- | :--- | :--- | :--- |
| **Engine** | V8 | V8 | JavaScriptCore |
| **I/O Modell** | libuv (Event Loop) | tokio (Rust) | Saját (Zig-based) |
| **Biztonság** | Nyitott (fs/net/env) | Sandbox (alapértelmezett) | Nyitott |
| **Standard Lib** | Minimalista (npm-függő) | Teljes (Web API-k) | Teljes (Web API-k) |
| **Package Mgmt** | npm | Built-in (deno.land/x) | Built-in (bun pm) |



## 2. Benchmark Metodika és Környezet

A mérések célja a futtatókörnyezetek startup idejének és CPU-intenzív feladatok (AES-GCM titkosítás) feldolgozási sebességének vizsgálata.

**Hardver specifikáció:**
- **CPU:** Intel Core i7-12700H (14 mag, 20 szál)
- **RAM:** 16GB DDR4
- **OS:** Windows 11 Pro 22H2
- **Runtime verziók:** Node.js v20.x, Deno v1.x, Bun v1.x

**Módszertan:**
- **JIT Bemelegedés:** A terheléses teszteket 10 másodperces "warm-up" szakaszok után értékeltük ki a V8/JSC JIT-fordítási effektusok normalizálása érdekében.
- **Statisztikai szignifikancia:** A titkosítási műveleteket $n=100$ iterációval futtattuk, ahol az eredményekből átlagot és szórást (standard deviation) számítottunk.
- **Latency mérés:** A `p97.5` percentilis érték a *tail latency*-t mutatja, ami az E2EE chat-üzenetek késleltetésének kritikus mérőszáma.

## 3. Technikai elemzés

1. **V8 vs JavaScriptCore:** Míg a Node.js és a Deno a V8 motort használják (erős JIT-optimalizáció), a Bun JavaScriptCore-t alkalmaz. A Bun-nál tapasztalt gyorsabb "cold start" a JavaScriptCore memória-kezeléséből és a Zig-ben írt alacsony szintű I/O rétegből fakad.
2. **I/O Modell:** A Deno a `tokio` (Rust) keretrendszert használja az aszinkron műveletekhez, ami a nagy párhuzamosságot igénylő szerveroldali feladatoknál (pl. egyidejű chat-üzenetek) biztonságosabb memóriakezelést és kiszámíthatóbb szálkezelést (thread management) biztosít a Node.js `libuv` implementációjával szemben.
3. **Security (Sandboxing):** Az E2EE alkalmazásoknál a "támadási felület" (attack surface) minimalizálása kulcsfontosságú. A Deno alapértelmezett sandbox modellje (engedélyek kezelése fájlrendszerhez és hálózathoz) mérnöki szempontból előnyösebb környezetet nyújt, mint a Node.js hagyományos, mindent engedélyező modellje.

## 4. Konklúzió és Döntés

Bár a **Bun** teljesítménye kiemelkedő a nyers HTTP throughput-ban, és a **Deno** architekturális biztonsága (sandboxing) ideális az E2EE-hez, a fejlesztési fázisban a **Node.js** mellett döntöttünk.

**Indoklás:**
A Node.js érett ökoszisztémája és a kriptográfiai könyvtárakhoz (pl. `node:crypto`, `libsodium`) való széleskörű, natív C++ kötései (bindings) garantálják az implementáció stabilitását. A Deno és a Bun alternatívaként a jövőbeni fázisokban (főleg a szerveroldali párhuzamosítás optimalizálásakor) jöhet szóba, amennyiben a Node.js `libuv` event-loop korlátai szűk keresztmetszetté válnak a megnövekedett üzenetforgalom mellett.