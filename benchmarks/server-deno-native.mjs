// server-deno-native.mjs
// Csak Deno-val fut: deno run --allow-net server-deno-native.mjs
// Deno saját, natív HTTP szerver API-ja (nem node:http kompatibilitási réteg)
Deno.serve({ port: 3000 }, async (req) => {
  if (req.method === 'POST') {
    const payload = new Uint8Array(await req.arrayBuffer());
    const decoded = btoa(String.fromCharCode(...payload));
    return new Response(JSON.stringify({ received: decoded.length }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }
  return new Response(null, { status: 404 });
});
console.log('Deno natív szerver fut: http://localhost:3000');
