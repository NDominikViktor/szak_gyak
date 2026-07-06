# Dokumentáció-generátorok összehasonlítása

A [jamstack.org/generators](https://jamstack.org/generators/) lista alapján
a legelterjedtebb, kifejezetten dokumentációra használt static site
generatorok:

| Eszköz | Nyelv/motor | Tanulási görbe | Erősség | Gyengeség |
|---|---|---|---|---|
| **MkDocs (+ Material)** | Python | nagyon alacsony | egyetlen YAML config, gyors beüzemelés, kiváló beépített keresés a Material témával | kevésbé rugalmas, ha komplex interaktív komponens kéne |
| **Docusaurus** | React/Node.js | közepes–magas | verziózás, i18n, MDX (React komponens Markdownban), erős közösség (Meta mögötte) | Node+React toolchain nehezebb, "túl sok" egy kis projektnek |
| **VuePress** | Vue/Node.js | közepes | Vue-alapú, jó ha valaki már ismeri a Vue-t, hasonló élmény mint a Docusaurus, csak Vue-val | kisebb közösség, mint a Docusaurus-nak, ami hatással lehet a témák és bővítmények elérhetőségére |
| **Hugo** | Go | magas | extrém gyors build, nagy (több ezer oldalas) dokumentációnál ideális, ahol a build idő szűk keresztmetszetté válhat | a Go template szintaxis nehézkes kezdőknek |

## Választás indoklása

A projekthez az **MkDocs + Material** kombináció mellett döntöttünk:

- egyszemélyes, kis léptékű dokumentációról van szó, nem kell a Docusaurus
  vagy Hugo által kínált skálázhatóság
- Python-alapú, egyetlen YAML konfigurációs fájllal működik — nem igényel
  külön Node.js build-láncot a dokumentációhoz, miközben a projekt maga
  Node.js-ben készül
- a Material téma önmagában hozza a beépített keresést és a
  MathJax/KaTeX-alapú képlet-megjelenítést, ami a benchmark-eredmények
  bemutatásához hasznos
- a betanulási görbe a legalacsonyabb a felsoroltak közül, ami egy nyári
  gyakorlat időkeretében fontos szempont
