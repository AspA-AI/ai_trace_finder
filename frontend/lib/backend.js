const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

export async function proxyRequest(request, path) {
  const incoming = new URL(request.url);
  const url = `${BACKEND_URL}${path}${incoming.search}`;
  const hasBody = !["GET", "HEAD"].includes(request.method);
  const upstream = await fetch(url, {
    method: request.method,
    headers: filterHeaders(request.headers),
    body: hasBody ? await request.arrayBuffer() : undefined,
    duplex: hasBody ? "half" : undefined,
  });
  return new Response(upstream.body, {
    status: upstream.status,
    headers: filterResponseHeaders(upstream.headers),
  });
}

function filterHeaders(headers) {
  const out = new Headers();
  for (const [key, value] of headers.entries()) {
    if (["host", "connection", "content-length"].includes(key.toLowerCase())) continue;
    out.set(key, value);
  }
  return out;
}

function filterResponseHeaders(headers) {
  const out = new Headers();
  for (const [key, value] of headers.entries()) {
    if (["transfer-encoding", "connection", "content-length"].includes(key.toLowerCase())) continue;
    out.set(key, value);
  }
  return out;
}
