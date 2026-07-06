# Szakmai gyakorlat dokumentáció

**Hallgató:** Novák Dominik Viktor
**Konzulens:** Piller Imre
**Helyszín:** Matematikai Intézet, Tanszék

## A projekt célja

A gyakorlat során egy célirányos, minimalista, végpontok között titkosított (E2EE)
üzenetküldő rendszer kerül megvalósításra, amely egy kisebb közösség vagy család saját
szerverén futtatható, mentesen a nagy szolgáltatókra jellemző reklámoktól, hírlevelektől
és követőkódoktól.

**Architektúra:**

- **Szerver:** Node.js alapú, kliens-szerver modell
- **Kliens:** sima HTML, CSS, JavaScript
- **Alapelvek:** nyílt, decentralizált, strukturált üzenetküldés (XMPP-elvek mentén)
- **Biztonság:** kliensoldali End-to-End Encryption (E2EE), WebCrypto API

**Kutatási/vizsgálati többlet:**

- A titkosítási réteg hatása a rendszer teljesítményére (üzenetméret és feldolgozási
  idő közötti összefüggés)
- Szerveroldali üzenetfeldolgozás terhelés alatt (throughput, latency)

## Dokumentum-struktúra

- [Munkanapló](worklog.md) — napi bontásban, mikor mivel foglalkoztunk
- **Kutatás / előkészítés** — a gyakorlat előkészítéseként kapott hat tétel
  (git, dokumentáció-generátorok, JavaScript/ECMAScript, futtatókörnyezetek,
  chat-alternatívák, titkosítás) összesítései
- [Benchmark](benchmarks/perf-hooks-example.md) — a teljesítmény- és memóriamérés
  kódpéldái és eredményei

**Első leadási határidő:** 2026.07.08. 8:00
