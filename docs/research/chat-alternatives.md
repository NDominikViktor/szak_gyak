# Chat alkalmazás alternatívák

**Cél:** hasonló, létező megoldások áttekintése ahhoz a tervezett
alkalmazáshoz, amely egy kis közösség/család számára készülő, saját
szerveren futtatható, minimalista, végpontok között titkosított
üzenetküldő rendszer, XMPP-elvekre építve.

## Protokoll szint

### XMPP

**Hivatalos oldal:** [xmpp.org](https://xmpp.org/) | **Szabvány:**
[RFC 6120](https://datatracker.ietf.org/doc/html/rfc6120) (core),
[RFC 6121](https://datatracker.ietf.org/doc/html/rfc6121) (IM)

1999-ben, eredetileg Jabber néven indult, azóta az IETF szabványosította,
és mára több mint 400 kiegészítő protokoll (XEP) épült rá. Az üzenetek
XML-alapú "stanza"-kban (`<message>`, `<presence>`, `<iq>`) közlekednek
egy folyamatosan nyitva tartott TCP-kapcsolaton keresztül. Ez pontosan az
az irány, amit a projekt is követ: könnyű, saját hosting-ra alkalmas,
decentralizált protokoll (federáció: különböző szerverek felhasználói
tudnak egymással kommunikálni, mint az e-mailnél).

Erőforrás-igénye kifejezetten alacsony — egy 1 GB RAM-os VPS-en egy XMPP
szerver a memória mindössze kb. 1,4%-át használta, míg egy ugyanott futó
Matrix szerver 27,7%-ot.

Az E2EE nála nem alapértelmezett, hanem az **OMEMO**
([XEP-0384](https://xmpp.org/extensions/xep-0384.html)) kiegészítésen
keresztül érhető el, ami a Signal Protocol Double Ratchet algoritmusára
épül, de XMPP-kompatibilis kulcscsere-mechanizmussal. A technikai
működés dióhéjban: minden eszköz publikál egy **kulcscsomagot**
("bundle") — egy Ed25519 azonosító kulcsot, egy aláírt PreKey-t, és
kb. 100 egyszer-használatos PreKey-t —, amit a **PEP**
([XEP-0163](https://xmpp.org/extensions/xep-0163.html), a Personal
Eventing Protocol) és a mögötte lévő **PubSub**
([XEP-0060](https://xmpp.org/extensions/xep-0060.html)) mechanizmuson
keresztül tesz közzé. Amikor egy másik felhasználó üzenetet szeretne
küldeni, lekéri ezt a csomagot, és ezzel indítja el az X3DH-szerű
kezdeti kulcscserét, amit aztán a Double Ratchet visz tovább — az
üzenettartalom titkosítására AES-256-CBC + HMAC-SHA256 kombinációt
használ. Mivel ez az egész a meglévő XMPP-infrastruktúrára (PubSub)
épül, **szinte semmilyen szerveroldali módosítást nem igényel** — ez
az egyik fő oka annak, hogy OMEMO-t viszonylag könnyű hozzáadni egy
meglévő XMPP-szerverhez. Mivel ez csak kiegészítés, egy szerver
teljesen szabványos maradhat úgy is, hogy sosem támogatja az OMEMO-t.
Népszerű szerver-implementációk: [Prosody](https://prosody.im/),
[ejabberd](https://www.ejabberd.im/).

Az [1. ábra](#1-abra) a fent leírt lépéseket foglalja össze, a
visszaigazolásokkal (ack/receipt) együtt — a valóságban ez sem
egyirányú: a szerver és a felek is nyugtázzák az egyes lépéseket:

```mermaid
%%{init: {"theme": "base", "themeVariables": {
  "signalColor": "#e6e6e6",
  "signalTextColor": "#e6e6e6",
  "actorLineColor": "#e6e6e6",
  "actorBorder": "#7ea6d8",
  "actorBkg": "#1f2937",
  "actorTextColor": "#f0f3f7",
  "labelBoxBorderColor": "#7ea6d8",
  "labelBoxBkgColor": "#1f2937",
  "labelTextColor": "#f0f3f7",
  "loopTextColor": "#f0f3f7",
  "noteBkgColor": "#3d5573",
  "noteTextColor": "#f0f3f7",
  "noteBorderColor": "#7ea6d8",
  "activationBorderColor": "#e0994f",
  "activationBkgColor": "#3d5573"
}}}%%
sequenceDiagram
    participant K as Küldő kliens
    participant Sz as XMPP szerver (PubSub/PEP)
    participant C as Címzett kliens

    C->>Sz: 1. Kulcscsomag (bundle) publikálása<br/>(identitáskulcs + aláírt PreKey + ~100 egyszeri PreKey)
    Sz-->>C: ack (tárolva)
    K->>Sz: 2. Bundle lekérése (XEP-0060 / XEP-0163)
    Sz-->>K: bundle (egy egyszeri PreKey elhasználva)
    Note over K: 3. X3DH kulcscsere - közös titok létrehozása
    K->>Sz: 4. Első üzenet (Double Ratchet init + ciphertext)
    Sz->>C: üzenet továbbítása
    C-->>Sz: delivery receipt (XEP-0184)
    Sz-->>K: receipt továbbítása
    Note over K,C: 5. Minden további üzenetnél új ratchet-lépés<br/>(forward secrecy: régi kulcs nem fejt vissza újat)
```

**<a id="1-abra"></a>1. ábra:** OMEMO (XMPP) üzenetküldés folyamata,
optimista eset (a hibás esetekre lentebb).

!!! warning "Hibás esetek kezelése"
    Az [1. ábra](#1-abra) a protokoll szabály szerinti, hibamentes lefutását
    mutatja. A gyakorlatban legalább három hibaosztályt kell kezelni:

    - **A címzett offline, nincs aktív kapcsolata.** A szerver ilyenkor
      nem tud azonnal `delivery receipt`-et adni — az XMPP szerver a
      stanza-t eltárolja (offline message storage), és a címzett
      következő bejelentkezésekor kézbesíti. A küldő oldalán emiatt a
      "megérkezett" állapot csak a receipt tényleges megérkezésekor áll
      be, nem a küldés pillanatában.
    - **Elfogyott az egyszeri PreKey-kollekció.** Ha a bundle-ben nem
      maradt felhasználható PreKey, az X3DH kulcscsere nem tud lezajlani
      "perfect forward secrecy" móddal — a kliensnek ilyenkor vagy meg
      kell várnia, amíg a címzett frissíti a bundle-jét (ez a felelőssége
      a kliensnek, alacsony PreKey-szám esetén automatikusan újratölteni
      a listát), vagy a bundle csak az aláírt PreKey-t használja fel
      (gyengébb garanciával).
    - **Session-desync** (pl. a kliens törölte/elvesztette a helyi
      ratchet-állapotot, de a másik fél még a régi állapottal
      titkosít). Ilyenkor a dekódolás hibával tér vissza; a gyakorlatban
      ez egy explicit "session invalid" jelzést vált ki, ami egy új X3DH
      kulcscserét indít el (2-4. lépés megismétlése).

A [2. ábra](#2-abra) ugyanezt a három hibaesetet folyamatábraként,
döntési pontokként mutatja — minden elágazás egy rombusz (döntési
csomópont) kimenete, a hibaágak sem kivételek: a fogadó oldali
dekódolási hiba is egy külön döntési ponton keresztül vezet a
helyreállítási lépéshez, nem közvetlenül egy műveleti dobozból:

```mermaid
%%{init: {"theme": "base", "themeVariables": {
  "lineColor": "#e6e6e6",
  "textColor": "#f0f3f7",
  "mainBkg": "#1f2937",
  "nodeBorder": "#7ea6d8",
  "clusterBkg": "#1f2937"
}}}%%
flowchart TD
    A[Üzenet küldése] --> B{Van aktív<br/>Double Ratchet<br/>session?}
    B -->|igen| C[Titkosítás,<br/>ratchet-lépés]
    B -->|nem| D{Van elérhető<br/>PreKey a bundle-ben?}
    D -->|igen| E[X3DH kulcscsere,<br/>session létrehozása]
    D -->|nem| F[Hiba: bundle frissítés<br/>szükséges]
    E --> C
    C --> G{Címzett<br/>online?}
    G -->|igen| H[Azonnali kézbesítés]
    G -->|nem| I[Offline tárolás,<br/>kézbesítés bejelentkezéskor]
    H --> K{Fogadó oldali<br/>dekódolás sikeres?}
    I --> K
    K -->|igen| L[Üzenet megjelenítve<br/>+ receipt]
    K -->|nem| J[Session invalid,<br/>új X3DH indítása]
```

**<a id="2-abra"></a>2. ábra:** OMEMO üzenetküldés döntési logikája, a
hibaágakkal.

!!! note "Formális protokoll-verifikáció"
    Elméleti szempontból az is vizsgálható lenne, hogy a fenti
    döntésfa lefedi-e az összes lehetséges állapot/esemény
    kombinációt (pl. modell-ellenőrzéssel, mint amit a Signal-protokoll
    formális verifikációs munkái is alkalmaznak — ld. Cohn-Gordon,
    K., Cremers, C., Dowling, B., Garratt, L., & Stebila, D.: *A
    Formal Security Analysis of the Signal Messaging Protocol*, IEEE
    EuroS&P 2017, később bővített változat: *Journal of Cryptology*
    33, 2020). Ez jelenleg nem része a projektnek, de érdekes
    továbblépési irány lehetne a "titkosítási protokollok elméleti
    vizsgálata" témába, ha arra esne a választás.

### Matrix

**Hivatalos oldal:** [matrix.org](https://matrix.org/) | **Specifikáció:**
[spec.matrix.org](https://spec.matrix.org/)

Újabb protokoll, esemény-alapú architektúrával: minden szoba egy
eseménygráf (DAG - Directed Acyclic Graph), amit a résztvevő szerverek
egymás között replikálnak (hasonló elven, mint egy elosztott adatbázis).
Az E2EE-t az **Olm** (páronkénti, 1:1 munkamenetekhez, a Signal Protocol
Double Ratchet-jének implementációja) és a **Megolm** (csoportos
szobákhoz optimalizált) algoritmusok biztosítják, alapból bekapcsolva.
A Megolm technikailag eltér az OMEMO/Signal megközelítéstől: nem
minden résztvevőhöz külön Double Ratchet munkamenetet tart fenn (ami
egy 200 fős szobában 199 külön munkamenetet jelentene), hanem **egy
közös, csak-előre-forgatható (one-way) racsnit** használ szobánként és
küldő eszközönként — ezt a kezdeti kulcsot Olm-on keresztül,
titkosítva osztja meg minden résztvevővel. Ennek következménye egy
tudatos biztonsági kompromisszum: aki megszerzi egy adott ponton a
racsni állapotát, **onnantól előre** tud minden üzenetet visszafejteni
(amíg a kliens újra nem indítja a munkamenetet), viszont a korábbi
üzeneteket nem — ez gyengébb garancia, mint az OMEMO/Signal
üzenetenkénti kulcsváltása, cserébe nagy létszámú szobáknál
számításigényben sokkal hatékonyabb. Erős a hídépítő (bridging)
képessége más platformok (Discord, Telegram, IRC) felé. Cserébe jóval
nagyobb erőforrást igényel, és a hivatalos szerver-szoftver
([Synapse](https://github.com/element-hq/synapse)) admin oldalról
nehézkesebb, mint az XMPP szerverek — újabb, könnyebb implementációk
(pl. [Conduit](https://conduit.rs/)) ezen próbálnak javítani.

A [3. ábra](#3-abra) a Megolm session-kulcs terjesztésének és a
csoportos titkosításnak a folyamatát mutatja, a szoba többi tagjának
visszaigazolásaival együtt:

```mermaid
%%{init: {"theme": "base", "themeVariables": {
  "signalColor": "#e6e6e6",
  "signalTextColor": "#e6e6e6",
  "actorLineColor": "#e6e6e6",
  "actorBorder": "#7ea6d8",
  "actorBkg": "#1f2937",
  "actorTextColor": "#f0f3f7",
  "labelBoxBorderColor": "#7ea6d8",
  "labelBoxBkgColor": "#1f2937",
  "labelTextColor": "#f0f3f7",
  "loopTextColor": "#f0f3f7",
  "noteBkgColor": "#3d5573",
  "noteTextColor": "#f0f3f7",
  "noteBorderColor": "#7ea6d8",
  "activationBorderColor": "#e0994f",
  "activationBkgColor": "#3d5573"
}}}%%
sequenceDiagram
    participant K as Küldő kliens
    participant Sz as Home szerver (esemény-DAG)
    participant T as Szoba többi tagja

    K->>Sz: 1. Olm páronkénti session felépítése (ha még nincs)
    Sz->>T: session-ajánlat továbbítása
    T-->>Sz: session ack
    Sz-->>K: session ack
    Note over K: 2. Megolm session-kulcs generálása<br/>(szobánként + küldő eszközönként egy)
    K->>Sz: 3. Session-kulcs, Olm-mal titkosítva
    Sz->>T: session-kulcs továbbítása (m.room_key)
    T-->>Sz: ack
    K->>Sz: 4. Üzenet, Megolm-mal titkosítva (közös racsni)
    Sz->>T: esemény terjesztése (DAG-ba fűzve)
    T-->>Sz: m.receipt (olvasási visszaigazolás)
    Sz-->>K: receipt továbbítása
```

**<a id="3-abra"></a>3. ábra:** Matrix (Olm/Megolm) — csoportos
üzenetküldés folyamata (optimista eset).

Jól látszik a különbség az OMEMO-hoz ([1. ábra](#1-abra)) képest: ott
minden üzenethez páronkénti ratchet-lépés történik, itt egy szobánkénti
közös racsni-kulcsot osztanak meg egyszer, Olm-mal titkosítva.

!!! warning "Hibás esetek kezelése"
    - **Új tag csatlakozik a szobához, miután már folyt a beszélgetés.**
      Az új tag nem kapja meg visszamenőleg a régi Megolm-kulcsot
      (ez tudatos tervezési döntés, ld. "előre-forgatható racsni" a
      szöveg elején) — a korábbi üzeneteket csak akkor tudja
      visszafejteni, ha valamelyik meglévő tag explicit megosztja vele
      a "key export"-ot. Ez a Matrix egyik ismert korlátja: nincs
      automatikus "history sharing" alapértelmezésben.
    - **Eszköz-verifikáció sikertelen** (a küldő nem tudja megbízhatóan
      azonosítani a címzett eszközét). A kliens ilyenkor "unverified
      device" figyelmeztetést jelenít meg, de a Matrix — biztonság
      helyett elérhetőséget priorizálva — alapból **mégis elküldi** az
      üzenetet, csak jelzi a bizonytalanságot; ez explicit
      felhasználói döntés kérdése, nem protokollhiba.
    - **A home szerver ideiglenesen elérhetetlen.** Mivel az
      esemény-DAG elosztott (több home szerver replikálja), a küldő
      kliens a helyi (saját) szerverére küldi az eseményt, ami
      pufferolja és később, a kapcsolat helyreállásakor szinkronizálja
      a többi szerverrel (federation retry) — ez a Matrix föderált
      architektúrájának közvetlen következménye, az OMEMO-nál nincs
      ilyen többszintű újrapróbálkozási mechanizmus.

### Signal

**Hivatalos oldal:** [signal.org](https://signal.org/) | **Protokoll
dokumentáció:**
[signal.org/docs](https://signal.org/docs/)

A legelterjedtebb, iparági referenciának számító E2EE megoldás — innen
ered a Signal Protocol/Double Ratchet is, amit az XMPP OMEMO és a Matrix
Olm/Megolm is átvett. Nem alkalmas viszont a projekt céljaira, mert
alapvetően centralizált: a Signal szervere zárt forráskódú, nincs
hivatalos, interoperábilis módja annak, hogy valaki saját szerveren
futtassa, kompatibilis módon a hivatalos Signal-hálózattal.

### Kisebb, kevésbé elterjedt alternatívák

- **[Session](https://getsession.org/)** — Signal-fork, decentralizált,
  Oxen blokklánc-alapú üzenettovábbítással (nincs központi szerver)
- **[Briar](https://briarproject.org/)**, **[Tox](https://tox.chat/)** —
  peer-to-peer megoldások, alacsony elterjedtség
- **[Delta Chat](https://delta.chat/)** — e-mail alapú (SMTP/IMAP fölé
  épített E2EE réteg, Autocrypt szabvánnyal), bárkinek van már e-mail
  címe, de a szolgáltatók nem-szabványos implementációi miatt
  kompatibilitási problémák adódhatnak

## Konkrét alkalmazás szint

| Alkalmazás/szoftver | Link | Típus | Titkosítás | Miben hasonlít a projekthez |
|---|---|---|---|---|
| **Snikket** | [snikket.org](https://snikket.org/) | Előre konfigurált, Docker-alapú XMPP szerver | OMEMO (alapból bekapcsolva) | Pontosan erre a célra készült: család/baráti kör könnyen üzemeltetheti saját szerveren, minimális beállítással |
| **Conversations / Dino** | [conversations.im](https://conversations.im/) / [dino.im](https://dino.im/) | XMPP kliens (Android / desktop) | OMEMO | Snikket vagy saját Prosody/ejabberd szerverrel párosítva funkcionálisan nagyon közel áll a tervezett rendszerhez |
| **Element** | [element.io](https://element.io/) | Matrix kliens | Olm/Megolm | Letisztult, több platformos, self-hosted szerverrel (Synapse/Conduit) családi körben is használt |
| **SimpleX Chat** | [simplex.chat](https://simplex.chat/) | Fiók/telefonszám nélküli üzenetküldő | Double Ratchet | Minimalista, identitás nélküli filozófia — inspiráció a letisztult felhasználói élményhez |
| **Rocket.Chat / Zulip / Mattermost** | [rocket.chat](https://rocket.chat/) / [zulip.com](https://zulip.com/) / [mattermost.com](https://mattermost.com/) | Csapat-kommunikációs platformok | opcionális/plugin-függő | Szintén self-hosted, nyílt forráskódú, de jóval nagyobb léptékű — jó ellenpélda arra, miben szeretnénk egyszerűbbek maradni |

## Következtetés a projekthez

A legközelebbi analógia a **Snikket + Conversations/Dino** kombináció: kis
léptékű, saját szerver, gyors telepítés, XMPP-alapú, OMEMO titkosítással.

A tervezett projekt ennek egy saját fejlesztésű, Node.js-alapú, webes
(HTML/JS kliens) változata, ugyanazokkal az alapelvekkel (nyílt,
decentralizált, strukturált üzenetküldés), a Rocket.Chat/Zulip/Mattermost-féle
nehezebb platformoknál jóval egyszerűbb, minimálisabb célkitűzéssel.

A tervezett rendszer komponenseinek felépítése az
[Architektúra](../architecture.md) oldalon található ábrán látható.
