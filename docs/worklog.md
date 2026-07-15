# Munkanapló

| Dátum | Kezdés | Vég | Típus | Feladat |
|---|---|---|---|---|
| 2026-07-02 | 13:00 | 13:40 | setup | MkDocs + mkdocs-material telepítése, Windows PATH-probléma megoldása |
| 2026-07-02 | 13:40 | 14:20 | setup | Projektstruktúra létrehozása, `mkdocs.yml` konfigurálása Material témával |
| 2026-07-02 | 14:20 | 15:30 | research | Git branch-stratégiák áttekintése (trunk-based, git flow, github flow) |
| 2026-07-02 | 15:30 | 16:00 | writing | Git workflow összefoglaló megírása |
| 2026-07-02 | 16:00 | 17:00 | research | Dokumentáció-generátorok áttekintése (MkDocs, Docusaurus, VuePress, Hugo) |
| 2026-07-02 | 17:00 | 17:30 | writing | Doc-generátor összehasonlítás megírása |
| 2026-07-02 | 17:30 | 20:37 | research | JavaScript nyelv / ECMAScript szabványok áttekintése (ES5-ES2020) |
| 2026-07-03 | 14:00 | 15:00 | research | Node.js vs. Deno vs. Bun - benchmark-források összevetése |
| 2026-07-03 | 15:00 | 15:30 | writing | Node/Deno/Bun összefoglaló megírása |
| 2026-07-03 | 15:30 | 17:00 | research | Chat alkalmazás alternatívák - protokoll szint (XMPP, Matrix, Signal) |
| 2026-07-03 | 17:00 | 18:00 | research | Chat alkalmazás alternatívák - konkrét alkalmazások |
| 2026-07-03 | 18:00 | 18:30 | writing | Chat alternatívák összesítés megírása |
| 2026-07-03 | 18:30 | 19:12 | research | Titkosítási algoritmusok/könyvtárak áttekintése |
| 2026-07-04 | 10:00 | 10:30 | writing | Titkosítás összesítés véglegesítése |
| 2026-07-04 | 10:30 | 11:30 | coding | `perf_hooks` alapú titkosítási benchmark szkript megírása |
| 2026-07-04 | 11:30 | 12:15 | coding | `autocannon` HTTP terheléses teszt szkript megírása |
| 2026-07-04 | 12:15 | 12:45 | measurement | Eredmények rögzítése, értelmezése |
| 2026-07-06 | 16:15 | 17:00 | setup | Repository szerkezet javítása (redundáns almappa eltávolítása) |
| 2026-07-06 | 17:00 | 18:00 | setup | Git history granuláris újraépítése (Conventional Commits, angol nyelv) |
| 2026-07-06 | 18:00 | 18:15 | setup | `requirements.txt` hozzáadása |
| 2026-07-06 | 18:15 | 18:45 | setup | GitHub Pages beállítása (`mkdocs gh-deploy`) |
| 2026-07-06 | 18:45 | 19:15 | writing | README és git-workflow dokumentáció frissítése |
| 2026-07-06 | 20:30 | 22:00 | measurement | Deno és Bun telepítése, benchmark újrafuttatása mindhárom runtime-on |
| 2026-07-06 | 22:00 | 22:30 | writing | Node/Deno/Bun dokumentum frissítése valós mérésekkel, statisztikai ellenőrzés |
| 2026-07-07 | 22:30 | 23:40 | writing | Chat-alternatívák dokumentum kiegészítése protokoll- és titkosítási részletekkel (OMEMO, Olm/Megolm), titkosítási kutatás referenciákkal bővítve |
| 2026-07-07 | 23:40 | 23:55 | writing | JavaScript/ECMAScript összefoglaló kiegészítése TypeScript-áttekintéssel; munkanapló egységes táblázat formátumra alakítása |
| 2026-07-07 | 23:55 | 00:14 | coding | Runtime benchmark kiterjesztése 10 MB/100 MB méretekig, JIT warm-up kiszűrés implementálása, natív szerver API-k (Deno.serve, Bun.serve) hozzáadása |
| 2026-07-08 | 21:30 | 22:23 | writing | Rendszerarchitektúra oldal és ábra elkészítése (1. konzulensi visszajelzésre reagálva) |
| 2026-07-08 | 22:23 | 22:23 | writing | Lineáris regressziós modell, 95%-os konfidencia-intervallumos ábra, warm-up-elemzés és ábraszámozás hozzáadása a runtime benchmarkhoz |
| 2026-07-08 | 22:23 | 22:23 | writing | Kulcskezelési szakasz és magyar nyelvű Double Ratchet hivatkozás hozzáadása, OMEMO/Megolm technikai részletek mélyítése |
| 2026-07-08 | 22:23 | 22:43 | measurement | Kettes-hatvány alapú (128 B - 64 MiB) mérési sorozat hozzáadása módszertani finomításként |
| 2026-07-10 | 19:00 | 19:20 | writing | 2. konzulensi visszajelzés feldolgozása: matplotlib-szkriptek (`generate_charts.py`, `generate_diagrams.py`) pótlása a repóba, mert korábban csak a kész `.png`-k kerültek be, a generáló kód nem |
| 2026-07-10 | 19:20 | 19:50 | coding | Benchmark szkriptek (`encrypt-benchmark-v2.mjs`, `-v3-pow2.mjs`) kiegészítése: iterációszámok kitevős alakra formázva és méret alapján számolva (nem hardcode-olt táblázat), `--csv`/`--raw-samples`/`--iteration-multiplier` kapcsolók a gépfüggetlen, reprodukálható méréshez |
| 2026-07-10 | 19:50 | 20:15 | writing | Architektúra-ábra szimmetrikus átrajzolása (két kliens oldalt, szerver alul/középen), üzenetfogadás és eseménykezelés szakasz hozzáadása |
| 2026-07-10 | 20:15 | 20:35 | writing | OMEMO és Matrix (Olm/Megolm) protokoll-kommunikációs ábrák elkészítése és beillesztése a chat-alternatívák oldalba |
| 2026-07-10 | 20:35 | 20:50 | writing | Ábraszámozás átállítása oldalankénti (nem globális) számozásra |
| 2026-07-10 | 20:50 | 21:15 | coding | `scripts/run-pipeline.mjs` - egylépéses mérés → chart → dokumentum-build pipeline elkészítése (Node.js-ben, Windows/Git Bash kompatibilitás miatt) |
| 2026-07-10 | 21:15 | 21:25 | writing | Munkanapló kiegészítése a 07-07/07-08-i és a jelen munkamenet bejegyzéseivel |
| 2026-07-10 | 21:25 | 21:45 | measurement | Pipeline lefuttatása saját gépen (Node.js), friss mérési eredmények és warm-up-szemléltető ábra generálása valós adatból |
| 2026-07-10 | 21:45 | 22:00 | other | Git történet rendberakása (rövid, egysoros commit-üzenetek), `mkdocs gh-deploy` a GitHub Pages frissítéséhez |
| 2026-07-13 | 18:30 | 19:30 | writing | 2. visszajelzési kör (3. üzenet) feldolgozása: architektúra- és protokoll-ábrák Mermaid diagramra cserélve (korábbi matplotlib-ábrák nyíl/kontraszt-hibái, szekvenciadiagram-igény miatt); pipeline adatfolyam-ábra hozzáadása |
| 2026-07-13 | 19:30 | 19:50 | writing | Ábraszámozási hiba javítása node-deno-bun.md-ben (a warm-up chart fizikailag előbb szerepelt, mint a titkosítási chart, de "2. ábra" volt ráírva "1." helyett); warm-up-szemléltető ábra beillesztése |
| 2026-07-13 | 19:50 | 20:05 | coding | Lineáris regressziós illesztés hozzáadása a titkosítási chart-hoz (`generate_charts.py`), a táblázatos becslés vizuális megerősítéseként |
| 2026-07-15 | 18:30 | 19:00 | writing | 3. visszajelzési kör feldolgozása: architektúra-ábra pontosítása (kétirányú, címkézett belső nyilak; konkrét Relay-ACC útvonal), ábra/táblázat-hivatkozások számmal és anchor-linkkel |
| 2026-07-15 | 19:00 | 19:20 | writing | Hibás esetek kezelésének hozzáadása mindkét protokollhoz (OMEMO: offline címzett, elfogyott PreKey, session-desync; Matrix: késői csatlakozás, eszköz-verifikáció, szerver-elérhetetlenség); mermaid init-fix próba a nyílhegy-láthatósághoz |
| 2026-07-15 | 19:20 | 19:35 | coding | Automatikus szakasz-számozás (CSS counter, `docs/stylesheets/numbering.css`), fejezetcímek kézi számozásának eltávolítása |
| 2026-07-15 | 19:35 | 19:50 | writing | Táblázatok számozása és linkelt hivatkozása (7 táblázat), pipeline-ábra megcímkézése |
| 2026-07-15 | 19:50 | 20:20 | coding | Regressziós modell hibájának feltárása (OLS-t a legnagyobb méretű pont dominálta, Deno-nál negatív, fizikailag értelmetlen rezsi-becslést adva) és javítása relatív hibára súlyozott illesztéssel; kiugró-érték vs. tartós warm-up elemzés és eloszlás-vizsgáló ábra (`plot_distribution`) hozzáadása |
| 2026-07-15 | 20:20 | 20:25 | writing | Racsni/Double Ratchet terminológia-magyarázat beillesztése magába a dokumentációba |
| 2026-07-15 | 20:25 | 20:30 | writing | Munkanapló kiegészítése a mai munkamenettel |

!!! note "Időbélyegek pontossága"
    A 2026-07-07 és 2026-07-08-i sorok a git commit-időbélyegek alapján lettek
    rekonstruálva utólag (a munkamenet közben nem lett minden lépés azonnal
    naplózva) - ezért a kezdés/vég időpontok közelítőek.
