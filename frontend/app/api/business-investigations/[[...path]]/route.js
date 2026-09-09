import { proxyRequest } from "../../../../lib/backend";

async function forward(request, { params }) {
  const resolved = await params;
  const path = (resolved.path || []).join("/");
  return proxyRequest(request, path ? `/business-investigations/${path}` : "/business-investigations");
}

export const GET = forward;
export const POST = forward;
