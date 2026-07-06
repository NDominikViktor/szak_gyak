# Chat alkalmazás alternatívák

**Cél:** hasonló, létező megoldások áttekintése ahhoz a tervezett
alkalmazáshoz, amely egy kis közösség/család számára készülő, saját
szerveren futtatható, minimalista, végpontok között titkosított
üzenetküldő rendszer, XMPP-elvekre építve.

## Protokoll szint

### XMPP

1999-ben, eredetileg Jabber néven indult, azóta az IETF szabványosította
(RFC 3920/3921, majd 6120/6121), és mára több mint 400 kiegészítő
protokoll (XEP) épült rá. Ez pontosan az az irány, amit a projekt is
követ: könnyű, saját hosting-ra alkalmas, decentralizált protokoll.

Erőforrás-igénye kifejezetten alacsony — egy 1 GB RAM-os VPS-en egy XMPP
szerver a memória mindössze kb. 1,4%-át használta, míg egy ugyanott futó
Matrix szerver 27,7%-ot — ami family/kisközösségi self-hosting esetén
jelentős különbség.

Az E2EE nála nem alapértelmezett, hanem az **OMEMO** kiegészítésen
keresztül érhető el, ami a Signal Protocol Double Ratchet algoritmusára
épül. Mivel ez csak kiegészítés, egy szerver teljesen szabványos maradhat
úgy is, hogy sosem támogatja az OMEMO-t — a titkosítás lefedettsége azon
múlik, milyen kliens-szerver kombinációt futtatnak a felhasználók.
Népszerű szerver-implementációk: **Prosody**, **ejabberd**.

### Matrix

Újabb protokoll, esemény-alapú architektúrával, ahol minden beszélgetés
egy elosztott adatbázisban tárolódik és a résztvevő szerverek között
replikálódik. Előnye, hogy az E2EE alapból, kikapcsolás nélkül aktív
minden csevegésben és privát szobában, és erős a hídépítő (bridging)
képessége más platformok felé. Cserébe jóval nagyobb erőforrást igényel,
és a hivatalos szerver-szoftver (Synapse) admin oldalról nehézkesebb,
kevesebb konfigurációs lehetőséggel, mint az XMPP szerverek.

### Signal

A legelterjedtebb, iparági referenciának számító E2EE megoldás — innen
ered a Signal Protocol/Double Ratchet is, amit az XMPP OMEMO és a Matrix
Olm/Megolm is átvett. Nem alkalmas viszont a projekt céljaira, mert
alapvetően centralizált: nincs hivatalos, interoperábilis módja annak,
hogy valaki saját szerveren futtassa, kompatibilis módon a hivatalos
Signal-hálózattal.

### Kisebb, kevésbé elterjedt alternatívák

- **Session** — Signal-fork, decentralizált, blokklánc-alapú
  üzenettovábbítással
- **Briar, Tox** — peer-to-peer megoldások, alacsony elterjedtség
- **Delta Chat** — e-mail alapú, bárkinek van már e-mail címe, de a
  szolgáltatók nem-szabványos implementációi miatt kompatibilitási
  problémák adódhatnak

## Konkrét alkalmazás szint

| Alkalmazás/szoftver | Típus | Miben hasonlít a projekthez | Miben más |
|---|---|---|---|
| **Snikket** | Előre konfigurált, Docker-alapú XMPP szerver | Pontosan erre a célra készült: család/baráti kör könnyen üzemeltetheti saját szerveren, minimális beállítással — ez a "referencia-termék" | Kész, letölthető termék, nem saját fejlesztésű kódbázis |
| **Conversations (Android) / Dino (desktop)** | XMPP kliens-alkalmazások | Snikket vagy saját Prosody/ejabberd szerverrel párosítva funkcionálisan nagyon közel áll a tervezett rendszerhez, OMEMO titkosítással | Kész kliensek, itt saját fejlesztés készül HTML/JS-ben |
| **Element** | Matrix kliens | Letisztult, több platformos, self-hosted szerverrel (Synapse/Conduit/Dendrite) családi körben is használt | A Matrix-háttér jóval nehezebb, erőforrás-igényesebb, mint az XMPP |
| **SimpleX Chat** | Fiók/telefonszám nélküli üzenetküldő | Minimalista, identitás nélküli filozófia — inspiráció a letisztult felhasználói élményhez | Nem klasszikus self-hosted családi chat, más architektúra (privát meghívó-linkek) |
| **Signal** | Központosított E2EE üzenetküldő | UX-referencia: letisztult, kizárólag üzenetküldésre fókuszáló felület | Nem self-hostolható |
| **Rocket.Chat / Zulip / Mattermost** | Csapat-kommunikációs platformok | Szintén self-hosted, nyílt forráskódú | Sokkal nagyobb léptékű, funkciógazdagabb (csatornák, integrációk) — jó ellenpélda arra, miben szeretnénk egyszerűbbek maradni |

## Következtetés a projekthez

A legközelebbi analógia a **Snikket + Conversations/Dino** kombináció: kis
léptékű, saját szerver, gyors telepítés, XMPP-alapú, OMEMO titkosítással.

A tervezett projekt ennek egy saját fejlesztésű, Node.js-alapú, webes
(HTML/JS kliens) változata, ugyanazokkal az alapelvekkel (nyílt,
decentralizált, strukturált üzenetküldés), a Rocket.Chat/Zulip/Mattermost-féle
nehezebb platformoknál jóval egyszerűbb, minimálisabb célkitűzéssel.
