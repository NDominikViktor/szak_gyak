# Szakmai gyakorlat — E2EE üzenetküldő rendszer

Nyári szakmai gyakorlat dokumentációja. A projekt egy célirányos,
minimalista, végpontok között titkosított (E2EE) üzenetküldő rendszer
fejlesztése, amely egy kisebb közösség vagy család saját szerverén
futtatható, XMPP-elvek (nyílt, decentralizált, strukturált
üzenetküldés) mentén.

**Hallgató:** Novák Dominik Viktor
**Konzulens:** Piller Imre
**Intézmény:** Matematikai Intézet

## 📖 Dokumentáció

**Élő dokumentáció:** [https://NDominikViktor.github.io/szak_gyak/](https://NDominikViktor.github.io/szak_gyak/)

A `docs/` mappa a dokumentáció *forrása* (Markdown fájlok), nem a végleges
megjelenítési forma — a fenti linken érhető el a lebuildelt, böngészhető
változat.

## A dokumentáció felépítése

A teljes dokumentáció [MkDocs](https://www.mkdocs.org/) segítségével
készült, a [Material for
MkDocs](https://squidfunk.github.io/mkdocs-material/) témával.

### Helyi futtatás

Szükséges: Python 3.

```bash
pip install mkdocs mkdocs-material
```

A repó gyökerében:

```bash
python -m mkdocs serve
```

Ezután a dokumentáció elérhető: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Statikus build generálása

```bash
python -m mkdocs build
```

A legenerált oldal a `site/` mappába kerül (ez nincs verziózva, lásd
`.gitignore`).

## Tartalom

- **[Kezdőlap](docs/index.md)** — a projekt célja, architektúrája
- **[Munkanapló](docs/worklog.md)** — napi bontásban, mikor mivel
  foglalkoztunk
- **Kutatás / előkészítés** (`docs/research/`)
    - Git workflow (branch-stratégiák, Conventional Commits)
    - Dokumentáció-generátorok összehasonlítása
    - JavaScript nyelv / ECMAScript szabványok
    - Node.js vs. Deno vs. Bun
    - Chat alkalmazás alternatívák (protokoll és konkrét alkalmazás szinten)
    - Titkosítási algoritmusok és könyvtárak (E2EE)
- **[Benchmark](docs/benchmarks/perf-hooks-example.md)** — teljesítmény-
  és memóriamérési kódpéldák és eredmények (`perf_hooks`, `autocannon`)

## Technológiai stack (tervezett)

- **Szerver:** Node.js
- **Kliens:** HTML, CSS, JavaScript
- **Titkosítás:** WebCrypto API (kliensoldali E2EE)
- **Dokumentáció:** MkDocs + Material
