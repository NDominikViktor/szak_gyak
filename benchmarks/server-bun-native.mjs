// server-bun-native.mjs
// Csak Bun-nal fut: bun run server-bun-native.mjs
// Bun saját, natív HTTP szerver API-ja (nem node:http kompatibilitási réteg)
Bun.serve({
  port: 3000,
  async fetch(req) {
    if (req.method === 'POST') {
      const payload = new Uint8Array(await req.arrayBuffer());
      const decoded = Buffer.from(payload).toString('base64');
      return new Response(JSON.stringify({ received: decoded.length }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return new Response(null, { status: 404 });
  },
});
console.log('Bun natív szerver fut: http://localhost:3000');
