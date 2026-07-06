# Dokumentáció-generátorok — technikai összehasonlítás

A cél annak eldöntése volt, melyik eszköz alkalmas legjobban technikai
dokumentációra, amelyben matematikai jelölésrendszer (képletek) és
verziókövetés-barát forrás egyaránt fontos szempont.

| Szempont | MkDocs (Material) | Docusaurus | VuePress | Hugo |
|---|---|---|---|---|
| **Renderelési modell** | statikus (Python/Jinja2) | reaktív (React/SPA) | reaktív (Vue/SPA) | statikus (Go) |
| **Függőségi lánc** | Python (pip), izolált a Node-alapú projekttől | Node.js (npm), komplex build-lánc | Node.js (npm), Vue-ökoszisztéma | Go (egyetlen bináris) |
| **Képletmegjelenítés** | natív (KaTeX/MathJax integráció) | plugin-függő (Remark-alapú) | plugin-függő | natív (Goldmark) |
| **Verziókövetés-barátság** | git-natív, tiszta Markdown fájlok | komplex (i18n, verziózási metaadatok) | közepes | fájl-alapú, tiszta |
| **Build pipeline** | egyszerű, determinisztikus | Webpack/Vite-alapú, nehezebb | Vite-alapú | rendkívül gyors, egyszerű bináris |

## A választás indoklása

**1) Build-lánc izoláció.** A projekt fejlesztői környezete Node.js-alapú
(a chat-alkalmazás szervere és kliense is JavaScript-ben készül). Egy
Python-alapú dokumentáció-generátor (MkDocs, `pip`-en keresztül)
teljesen elválasztja a dokumentáció build-folyamatát a projekt saját
függőségi fájától — ez elkerüli a lehetséges `node_modules`-konfliktusokat,
és determinisztikus, egyszerű build-folyamatot biztosít.

**2) SSR/hidratáció overhead.** A Docusaurus és a VuePress is
Single Page Application (SPA) architektúrát használ (React, illetve
Vue), ami "hidratációt" (kliensoldali runtime-inicializálást) igényel
minden oldalbetöltésnél. Az MkDocs ezzel szemben build-időben tiszta,
statikus HTML-t generál, ami jobb betöltési teljesítményt és jobb
keresőmotor-indexelhetőséget garantál, futásidejű JavaScript-függőség
nélkül.

**3) Matematikai pontosság.** A benchmark-eredmények (eloszlás, szórás,
percentilis) megbízható LaTeX-alapú képlet-megjelenítést igényelnek. Az
MkDocs Material natív KaTeX/MathJax-integrációt ad, ami megbízhatóan
működik — a Docusaurus/VuePress Remark-plugin-alapú megoldásainál
tapasztalt runtime JavaScript verziókonfliktusok nélkül.

**4) Verziókövetési hatékonyság.** Mivel a projekt trunk-based
fejlesztési modellt követ, a merge-konfliktusok feloldhatósága fontos
szempont. Az MkDocs a dokumentációt szigorúan Markdown fájlokban tárolja,
minimális metaadat-zajjal — ez tisztább, kezelhetőbb git diff-eket
eredményez, mint a sablon-nehéz vagy SPA-metaadat-gazdag alternatívák.

## A Hugo kimaradásának oka

A Hugo build-sebessége kiemelkedő, és több ezer oldalas
dokumentációknál ez döntő szempont lehet. Ennél a projektnél viszont a
dokumentáció mérete (néhány tucat oldal) miatt ez az előny nem
számottevő, ugyanakkor a Go template-szintaxis tanulása és a kevésbé
kiforrott matematikai jelölés-támogatás felesleges többletmunkát
jelentene egy ilyen léptékű projektnél.

## Végső döntés

**MkDocs + Material** — a build-lánc izolációja, a natív statikus HTML-
kimenet, a beépített matematikai jelölés-támogatás és a git-barát
Markdown-forrás együttesen ezt teszik a legmegfelelőbb választássá ehhez
a projekthez.
