import { proxyRequest } from "../../../../lib/backend";

async function forward(request, { params }) {
  const resolved = await params;
  return proxyRequest(request, `/investigations/${(resolved.path || []).join("/")}`);
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
