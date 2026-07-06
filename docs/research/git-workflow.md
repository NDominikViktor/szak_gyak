# Git workflow — branch-stratégiák

## Git Flow

Van egy fő fejlesztési ág (általában `develop` néven), szigorú hozzáféréssel.
A fejlesztők ebből az ágból hoznak létre további (feature) ágakat, és azokon
dolgoznak. Amikor egy funkció elkészül, a fejlesztő pull request-et (merge
request-et) nyit, amin keresztül a csapat kommentálhat, megbeszélheti a
változtatásokat. Ha minden rendben, az ág visszakerül (merge-elődik) a
`develop`-ba.

Amikor a `develop` elér egy kiadható állapotot, létrejön egy külön
release ág, amin a végső tesztelés és hibajavítás történik, egészen addig,
amíg a szoftver készen nem áll a felhasználóknak való kiadásra.

A Git Flow szigorú kontroll alatt áll: csak felhatalmazott fejlesztők
hagyhatják jóvá a módosításokat.

**Mikor érdemes használni:**

- nyílt forráskódú (open source) projekteknél
- amikor sok junior fejlesztő van a csapatban
- egy már bevált, éles terméknél

**Mikor okozhat problémát:**

- projekt indulásakor (szűk keresztmetszetet jelent)
- amikor gyors iterációra van szükség
- amikor a csapat főleg senior fejlesztőkből áll

## Trunk-based development

Itt egyetlen ág van, amin mindenki dolgozik — ezt hívják `main` (vagy trunk)
ágnak. A fejlesztők ebbe commitolják a kódjukat, és ez fut folyamatosan.
Előfordulhatnak nagyon rövid életű funkció-ágak, de ha a kód átmegy a
teszteken, azonnal a `main`-re kerül.

Ez biztosítja a folyamatos fejlesztést, és megakadályozza, hogy a
fejlesztőknek nehezen feloldható merge-konfliktusai legyenek — mivel
mindenki gyakran, kis lépésekben integrál. Cserébe nincs szigorú kontroll
afölött, hogy mi kerül be a forráskódba; az egyetlen védelmi vonal a
kód-review és az automatizált tesztek.

**Mikor érdemes használni:**

- projekt indulásakor, amikor a maximális fejlesztési sebesség a cél
- minimális formalitás mellett
- amikor gyors iterációra van szükség
- amikor főleg senior fejlesztőkkel dolgozik a csapat

**Mikor nem érdemes használni:**

- nyílt forráskódú projekteknél
- ha sok junior fejlesztő van a csapatban
- nagy csapat vagy már bevált, éles termék esetén

## GitHub Flow

Ez a Git Flow és a trunk-based development közötti köztes megoldás. Egyetlen
hosszú életű ág van, a `main`. A fejlesztők ebből hoznak létre rövid életű
funkció-ágakat, majd — miután a kód elkészült és megfelel a
minőségi elvárásoknak — visszamerge-elik azokat a `main`-be.

Nincs külön `develop`, `release` vagy `hotfix` ág, és a változtatások soha
nem kerülnek review nélkül a `main`-be. A GitHub Flow azt feltételezi, hogy:

- a `main` ág mindig production-kész állapotban van,
- minden változás kicsi és inkrementális,
- automatizált tesztek és CI/CD pipeline-ok garantálják a minőséget,
- akár egy napon belül is történhet több deployment.

Ez a workflow jól illik webalapú alkalmazásokhoz, ahol a folyamatos kiadás
(continuous delivery) a norma. Erősen támaszkodik viszont az automatizált
tesztekre és kiadási pipeline-okra, és feltételezi a gyakori, kis
változtatásokból álló fejlesztési kultúrát — a nagy, hosszú futású
funkciók problémát okozhatnak ebben a modellben.

## Választás a projekthez

Mivel ez egy egyszemélyes (hallgatói) projekt, a **trunk-based
development** egyszerűsített változata a legésszerűbb: rövid életű feature
branch-ek a `main` mellett, gyakori, kis commitokkal, [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) formátumban.

**Ez a projekt ténylegesen is így működik:** minden módosítás közvetlenül
(vagy rövid életű, gyorsan visszamerge-elt ágakon) a `main`-re kerül,
angol nyelvű, típusolt (Conventional Commits) commit üzenetekkel, egy-egy
logikai munkalépésre bontva (pl. `docs: ...`, `feat: ...`, `chore: ...`).
Ez látható is a repository commit history-jában.

## Conventional Commits

A [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
egy specifikáció a commit üzenetek egységes formázására, ami ember és gép
számára is egyértelmű jelentést ad nekik. A leggyakoribb típusok:

- `feat:` — új funkció
- `fix:` — hibajavítás
- `docs:` — csak dokumentáció-változás
- `refactor:` — kódszerkezet-változás funkcionális hatás nélkül
- `chore:` — karbantartási feladat (pl. build-konfiguráció)

Példa: `feat: felhasználói bejelentkezés WebSocket alapú session-kezeléssel`
