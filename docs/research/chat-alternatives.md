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
épül, de XMPP-kompatibilis kulcscsere-mechanizmussal (PEP - Personal
Eventing Protocol - segítségével teszi közzé a nyilvános kulcsokat).
Mivel ez csak kiegészítés, egy szerver teljesen szabványos maradhat úgy
is, hogy sosem támogatja az OMEMO-t. Népszerű szerver-implementációk:
[Prosody](https://prosody.im/), [ejabberd](https://www.ejabberd.im/).

### Matrix

**Hivatalos oldal:** [matrix.org](https://matrix.org/) | **Specifikáció:**
[spec.matrix.org](https://spec.matrix.org/)

Újabb protokoll, esemény-alapú architektúrával: minden szoba egy
eseménygráf (DAG - Directed Acyclic Graph), amit a résztvevő szerverek
egymás között replikálnak (hasonló elven, mint egy elosztott adatbázis).
Az E2EE-t az **Olm** (páronkénti, Double Ratchet-alapú) és **Megolm**
(csoportos beszélgetésekhez optimalizált, "ratchet-fa" struktúrájú)
algoritmusok biztosítják, alapból bekapcsolva. Erős a hídépítő
(bridging) képessége más platformok (Discord, Telegram, IRC) felé.
Cserébe jóval nagyobb erőforrást igényel, és a hivatalos szerver-szoftver
([Synapse](https://github.com/element-hq/synapse)) admin oldalról
nehézkesebb, mint az XMPP szerverek — újabb, könnyebb implementációk
(pl. [Conduit](https://conduit.rs/)) ezen próbálnak javítani.

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
