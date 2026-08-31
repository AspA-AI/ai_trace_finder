import { proxyRequest } from "../../../../lib/backend";

async function forward(request, { params }) {
  const resolved = await params;
  return proxyRequest(request, `/evaluations/${(resolved.path || []).join("/")}`);
}

export const GET = forward;
export const POST = forward;
