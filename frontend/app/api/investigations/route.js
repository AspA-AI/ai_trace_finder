import { proxyRequest } from "../../../lib/backend";

export async function POST(request) {
  return proxyRequest(request, "/investigations");
}

export async function GET(request) {
  return proxyRequest(request, "/investigations");
}
