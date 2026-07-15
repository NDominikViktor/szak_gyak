# Titkosítási algoritmusok és könyvtárak

## Alapfogalom: Signal Protocol / Double Ratchet

**Dokumentáció:** [signal.org/docs](https://signal.org/docs/)

Az iparágban de facto szabvánnyá vált E2EE-tervezési minta — nem konkrét
könyvtár, hanem egy algoritmus-család, amit a Signal, korábban a
WhatsApp, a Matrix (Olm/Megolm néven), valamint az XMPP (OMEMO
kiterjesztésen keresztül) is átvett.

**Hogyan működik röviden:** a felek egy kezdeti X3DH (Extended
Triple Diffie-Hellman) kulcscserével hoznak létre egy közös titkot, majd
minden egyes üzenetváltás után egy új Diffie-Hellman kulcspárt
generálnak, és ezzel "elforgatják" (ratchet) a titkosító kulcsot. Így ha
egy támadó megszerzi az aktuális kulcsot, azzal sem a korábbi, sem a
jövőbeli üzeneteket nem tudja visszafejteni — ezt hívják **forward
secrecy**-nek, illetve **post-compromise security**-nek (a jövőbeli
üzenetek védelme egy múltbeli kompromittálódás után is helyreáll).

## WebCrypto API

**Dokumentáció:** [MDN - Web Crypto
API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)

Böngészőbe (és Node.js-be is, a `crypto.webcrypto` objektumon keresztül)
beépített, natív titkosítási API, nem kell hozzá külön csomagot
telepíteni. Támogatott algoritmusok közül a projekthez relevánsak: az
**AES-GCM** (szimmetrikus, autentikált titkosítás — ezt használjuk a
[benchmark szkriptben](../benchmarks/perf-hooks-example.md) is) és az
**ECDH** (elliptikus görbés Diffie-Hellman kulcscsere, pl. P-256 görbével).
Előnye, hogy natívan gyors és biztonságos, mert a futtatókörnyezet
implementálja alacsony szinten. Hátránya, hogy elég alacsony szintű API
— mindenhol Promise-alapú, még egyszerű műveleteknél is —, és nem
támogat minden modern algoritmust (pl. az X25519 görbét csak újabb
böngészőverziók óta).

## libsodium (libsodium.js)

**Repó:** [github.com/jedisct1/libsodium.js](https://github.com/jedisct1/libsodium.js)

Szélesebb körben auditált, több nyelvben elérhető (C, WebAssembly-vel
JS-re fordítva) kriptográfiai könyvtár, magasabb szintű, kényelmesebb
API-val, mint a nyers WebCrypto. A Double Ratchet-hez szükséges
primitíveket kényelmesen kezeli: **X25519** (Curve25519-alapú
kulcscsere, gyorsabb és egyszerűbb, mint a WebCrypto P-256-ja) és
**ChaCha20-Poly1305** (AES-GCM alternatívája — szoftveres
implementációban gyakran gyorsabb, mert nem igényel hardveres AES
gyorsítást, ami relevánssá teszi kisebb/beágyazott eszközöknél). A teljes
csomag kb. 188 KB (minifikálva, gzip-elve), ami böngészős kliens esetén
már számottevő méret.

## Noble cryptography

**Repó:** [github.com/paulmillr/noble-ciphers](https://github.com/paulmillr/noble-ciphers)
(és testvér-csomagjai: `noble-hashes`, `noble-curves`)

Tisztán JavaScript-ben írt könyvtár-család, moduláris felépítéssel — egy
jó bundler csak azt a kódot húzza be, amire ténylegesen szükség van
(tree-shaking), szemben a libsodium egyben-jövő WASM-bináris méretével.
Ajánlott választás, amikor a WebCrypto nem fedi le az igényt (pl.
Curve25519/X25519 művelet régebbi böngészőkben).

## Node.js beépített `node:crypto` modul

**Dokumentáció:** [nodejs.org/api/crypto.html](https://nodejs.org/api/crypto.html)

Node 20+ óta jelentősen kényelmesebbé vált, és tartalmazza a
`crypto.webcrypto` objektumot is (ugyanaz az API, mint böngészőben). Van
rá 2026-os példa, hogy valaki teljesen külső függőség nélkül épített
E2EE-t vele (**Ed25519** hosszú távú identitáshoz — ez az EdDSA aláíró
algoritmus Curve25519 fölött, **X25519** ideiglenes session-kulcsokhoz) —
bár ilyenkor magának kell megoldania olyan dolgokat, mint a valódi
forward secrecy (kulcs-racsnizás) és a kulcscsere hitelesítése, amit egy
kész könyvtár már megad.

## Algoritmus-összehasonlítás

| Algoritmus | Típus | Hol használjuk | Megjegyzés |
|---|---|---|---|
| **AES-GCM** | szimmetrikus, autentikált titkosítás | üzenettartalom titkosítása | hardveres gyorsítással (AES-NI) nagyon gyors modern CPU-kon; ezt méri a [benchmark](../benchmarks/perf-hooks-example.md) |
| **ChaCha20-Poly1305** | szimmetrikus, autentikált titkosítás | AES-GCM alternatívája | szoftveresen gyakran gyorsabb, ha nincs hardveres AES-gyorsítás |
| **ECDH (P-256)** | aszimmetrikus kulcscsere | kezdeti közös titok létrehozása | WebCrypto natívan támogatja |
| **X25519 (Curve25519)** | aszimmetrikus kulcscsere | Double Ratchet kulcscsere lépései | gyorsabb és egyszerűbb, mint a P-256, de a WebCrypto csak újabban támogatja natívan |
| **Ed25519** | digitális aláírás | identitás-hitelesítés (kulcscsere aláírása) | EdDSA séma Curve25519 fölött |

## Kulcskezelés — hogyan kötődik a titkos kulcs a felhasználóhoz?

Mivel a kliens egy böngészőben futó alkalmazás, a hosszú távú titkos
kulcs alapesetben **az adott böngésző adott profiljához** kötődik: a
WebCrypto API a nem-exportálható (`extractable: false`) kulcsokat úgy
tárolja, hogy azok gyakorlatilag nem hagyhatják el azt a böngésző-
profilt, amelyben létrejöttek (IndexedDB-ben, a böngésző saját belső
tárolójában). Ez azt jelenti, hogy egy másik eszközön vagy böngészőben
megnyitva az alkalmazást, alapból **nincs hozzáférés a régi
üzenetekhez** — ami biztonsági szempontból jó (egy ellopott/elveszett
eszköz nem fér hozzá más eszközök kulcsaihoz), de használhatósági
szempontból korlátozó.

**Lehetséges megoldások a több eszközön való használatra** (ezek a
projektben még nincsenek eldöntve, ez egy tervezési kérdés, amit a
fejlesztés során kell megválaszolni):

1. **Exportálható kulcs + jelszóval védett biztonsági mentés** — a
   WebCrypto `exportKey()` függvényével a kulcs kiexportálható, majd egy
   felhasználó által megadott jelszóból származtatott kulccsal
   (`PBKDF2` vagy `Argon2`) titkosítva elmenthető (pl. egy fájlba vagy a
   szerverre, titkosított formában). Ez hasonló elven működik, mint a
   Signal "biztonsági mentés visszaállítási kulcsa" mechanizmusa.
2. **QR-kódos eszköz-párosítás** — egy már bejelentkezett eszköz
   megjelenít egy QR-kódot, amit az új eszköz beolvas, és ezen a
   csatornán (helyi hálózaton vagy a szerveren keresztül, de titkosítva)
   történik a kulcs átvitele. Ez a WhatsApp Web / Signal "linked
   devices" funkciójának elve.
3. **Több kulcspár eszközönként** — ahelyett, hogy ugyanazt a kulcsot
   vinnénk át, minden eszköz saját kulcspárt generál, és a régebbi
   eszköz(ök) "aláírják" (hitelesítik) az új eszköz nyilvános kulcsát —
   ez a Signal és a Matrix által is használt "device verification"
   megközelítés, ahol nem a titkos kulcs vándorol, hanem a bizalmi lánc
   épül tovább.

A projekt jelenlegi fázisában az **1. és 3. megoldás kombinációja**
tűnik a legreálisabbnak: kezdetben egyetlen eszköz/böngésző támogatása
az elsődleges cél, a több-eszközös support egy jövőbeli kiterjesztés
lenne.

## Ajánlás a projekthez

- **Kliens oldal (böngésző):** WebCrypto API az alap műveletekhez
  (AES-GCM üzenettitkosítás, ECDH kulcscsere)
- **Racsnizott kulcskezelés (Double Ratchet-szerű megoldás):** érdemes
  egy kész, auditált implementációt (pl. libsodium X25519 primitívjei)
  mintaként használni, és a saját racsni-logikát erre építeni. Egy magyar
  nyelvű, közérthető leírás a mechanizmusról: [Titok a zsebben — hogyan
  lett a Signal-protokoll a gigacsevegők láthatatlan
  testőre](https://geekhost.hu/titok-a-zsebben-hogyan-lett-a-signal-protokoll-a-gigacsevegok-lathatatlan-testore/)
  (a cikk a mechanizmust úgy írja le, hogy a Double Ratchet folyamatosan
  "csörlőzi", azaz előre forgatja a kulcsokat).

    !!! info "A 'kulcs-racsnizás' terminológia eredete"
        A "kulcs-racsnizás" kifejezés a saját tükörfordításunk az angol
        *Double Ratchet* mechanizmusra, mivel szabványos magyar
        szakkifejezés egyelőre nem létezik rá. A fent hivatkozott
        geekhost.hu forrás egyébként a "csörlőzés" szót használja
        ugyanerre a logikára — a két elnevezés ugyanazt a jelenséget
        írja le, csak más magyarítással.

  Saját tervezésű
  kriptográfiai algoritmus kitalálása helyett egy meglévő, auditált
  megoldásra érdemes építeni, mert az apró tervezési hibák
  kriptográfiában különösen nehezen vehetők észre, és súlyos biztonsági
  következményekkel járhatnak.
- **Szerver oldal:** végponti titkosításnál a szerver csak "vakon"
  továbbítja az adatot, így ott nincs szükség komoly kriptográfiai kódra,
  legfeljebb a metaadatok (feladó/címzett, időbélyeg) kezelésére
