# Titkosítási algoritmusok és könyvtárak

## Alapfogalom: Signal Protocol / Double Ratchet

Az iparágban de facto szabvánnyá vált E2EE-tervezési minta — nem konkrét
könyvtár, hanem egy algoritmus-család, amit a Signal, korábban a
WhatsApp, a Matrix (Olm/Megolm néven), valamint az XMPP (OMEMO
kiterjesztésen keresztül) is átvett.

A lényege a "ratchet" (racsni) mechanizmus: minden üzenetváltás után új
kulcsok generálódnak, így ha egy támadó megszerzi az aktuális kulcsot,
azzal sem a korábbi, sem a jövőbeli üzeneteket nem tudja visszafejteni —
ezt hívják **forward secrecy**-nek. Ezt érdemes mintaként követni a saját
E2EE modulban is.

## WebCrypto API

Böngészőbe (és Node.js-be is) beépített, natív titkosítási API, nem kell
hozzá külön csomagot telepíteni. Előnye, hogy natívan gyors és biztonságos,
mert a futtatókörnyezet implementálja alacsony szinten. Hátránya, hogy
elég alacsony szintű és kényelmetlen API — mindenhol Promise-alapú, még
egyszerű műveleteknél is. Elsősorban akkor optimális, ha a beépített
algoritmusok (AES-GCM, ECDH, RSA) pontosan lefedik az igényeket.

## libsodium (libsodium.js)

Szélesebb körben auditált, több nyelvben elérhető (C, WebAssembly-vel
JS-re fordítva) kriptográfiai könyvtár, magasabb szintű, kényelmesebb
API-val, mint a nyers WebCrypto. A Double Ratchet-hez szükséges
primitíveket (X25519 kulcscsere, ChaCha20-Poly1305) is kényelmesen
kezeli. A teljes csomag kb. 188 KB (minifikálva, gzip-elve), ami böngészős
kliens esetén már számottevő méret.

## Noble cryptography

Tisztán JavaScript-ben írt könyvtár-család (külön csomagok: ciphers,
hashes, curves, post-kvantum algoritmusok), moduláris felépítéssel — egy
jó bundler csak azt a kódot húzza be, amire ténylegesen szükség van
(tree-shaking). Ajánlott választás, amikor a WebCrypto nem fedi le az
igényt (pl. Curve25519/X25519 művelet, amit a WebCrypto natívan nem
támogat minden környezetben).

## Node.js beépített `node:crypto` modul

Node 20+ óta jelentősen kényelmesebbé vált. Van rá 2026-os példa, hogy
valaki teljesen külső függőség nélkül épített E2EE-t vele (Ed25519 hosszú
távú identitáshoz, X25519 ideiglenes session-kulcsokhoz) — bár ilyenkor
magának kell megoldani olyan dolgokat, mint a valódi forward secrecy
(kulcs-racsnizás) és a kulcscsere hitelesítése, amit egy kész könyvtár már
megad.

## Ajánlás a projekthez

- **Kliens oldal (böngésző):** WebCrypto API az alap műveletekhez
  (AES-GCM üzenettitkosítás, ECDH kulcscsere)
- **Racsnizott kulcskezelés (Double Ratchet-szerű megoldás):** érdemes egy
  kész, auditált implementációt (pl. libsodium X25519 primitívjei)
  mintaként használni, és a saját racsni-logikát erre építeni — saját
  tervezésű kriptográfiai algoritmust nem javasolt kitalálni, mert az
  könnyen hibázható
- **Szerver oldal:** végponti titkosításnál a szerver csak "vakon"
  továbbítja az adatot, így ott nincs szükség komoly kriptográfiai kódra,
  legfeljebb a metaadatok (feladó/címzett, időbélyeg) kezelésére
