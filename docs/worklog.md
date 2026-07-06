# Munkanapló

## 2026.07.02. (csütörtök)

**Időtartam:** 13:00 – 20:37 (kb. 7,5 óra, közte szünetekkel)

**Elvégzett feladatok:**

- MkDocs telepítése és beüzemelése (`pip install mkdocs mkdocs-material`,
  Windows PATH-probléma megoldása `python -m mkdocs` használatával)
- Alap projektstruktúra létrehozása (`mkdocs new`), `mkdocs.yml` konfiguráció
  összeállítása Material témával, MathJax/képlet-támogatással
- Git haladó szintű áttekintése: branch-stratégiák (trunk-based vs. Git Flow
  vs. GitHub Flow), interaktív git gyakorlás
- Statikus dokumentáció-generátorok összehasonlítása (MkDocs, Docusaurus,
  VuePress, Hugo) — indoklás az MkDocs Material választásra
- JavaScript nyelv / ECMAScript szabványok áttekintésének megkezdése
  (ES5 – ES2020, MDN guide alapján)

## 2026.07.03. (péntek)

**Időtartam:** 14:00 – 19:12

**Elvégzett feladatok:**

- Node.js vs. Deno vs. Bun összehasonlítás lezárása: két különböző, 2026-os
  benchmark-forrás adatainak összevetése, az eltérések okainak feltárása
  (szintetikus vs. valós terhelésű mérés), közös következtetések
  megfogalmazása
- Chat alkalmazás alternatívák összesítése két szinten:
    - protokoll szinten: XMPP, Matrix, Signal összehasonlítása
      (erőforrásigény, E2EE-alapértelmezettség, self-hosting nehézsége)
    - konkrét alkalmazás szinten: Snikket, Element, Conversations/Dino,
      SimpleX Chat, Signal, Rocket.Chat/Zulip/Mattermost áttekintése, és a
      legközelebbi analógia (Snikket + Conversations/Dino) azonosítása a
      saját projekthez
- Titkosítási algoritmusok/könyvtárak összesítése: Signal Protocol/Double
  Ratchet elve, WebCrypto API, libsodium, Noble cryptography, Node.js
  beépített `node:crypto` modul összehasonlítása, ajánlás a projekt
  kliens/szerver oldali titkosítási rétegéhez

## 2026.07.04. (szombat)

**Elvégzett feladatok:**

- JS teljesítmény/memória mérés kódpéldáinak elkészítése és futtatása:
    - `perf_hooks` alapú mérés a titkosítási művelet idejéről különböző
      üzenetméreteknél
    - `autocannon` terheléses teszt egy egyszerű HTTP szerveren, két
      egymást követő futtatással (JIT-bemelegedés megfigyelése)
- Ezzel a tanszéki előkészítő feladatlista technikai pontjai lezárultak

**Következő lépések:**

- Az összegyűjtött anyagok végleges MkDocs oldalakká rendezése (folyamatban,
  ez a dokumentáció maga)
- Feltöltés a repóba, majd jelzés a konzulensnek
