import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE_NAME } from "./lib/constants";

/**
 * Contrôle d'accès optimiste (recommandation Next.js) : on vérifie seulement
 * la présence du cookie ici. La vérification cryptographique réelle est faite
 * dans le layout serveur protégé (src/app/(app)/layout.tsx).
 */
export function proxy(request: NextRequest) {
  const hasCookie = Boolean(request.cookies.get(COOKIE_NAME)?.value);
  if (!hasCookie) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("from", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  // S'applique à tout sauf : assets Next, favicon, la page de login, et tout
  // fichier statique (chemins contenant un point, ex. /brand.svg).
  matcher: ["/((?!_next/static|_next/image|favicon.ico|login|.*\\.).*)"],
};
