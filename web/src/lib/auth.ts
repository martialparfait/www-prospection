import "server-only";
import { cookies } from "next/headers";
import { COOKIE_NAME } from "./constants";

const SESSION_DAYS = 7;

function getSecret(): string {
  const s = process.env.AUTH_SECRET;
  if (!s) throw new Error("AUTH_SECRET manquant.");
  return s;
}

/**
 * Jeton déterministe = HMAC-SHA256(AUTH_SECRET, marqueur).
 * La valeur n'est pas devinable sans AUTH_SECRET, et ne contient pas le mot de passe.
 */
export async function signToken(): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(getSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    enc.encode("www-prospection-auth-v1")
  );
  return Buffer.from(new Uint8Array(sig)).toString("base64url");
}

export async function verifyToken(value: string | undefined): Promise<boolean> {
  if (!value) return false;
  const expected = await signToken();
  // comparaison à temps constant
  if (value.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < value.length; i++)
    diff |= value.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

/** Vérification réelle (à utiliser dans le layout protégé, runtime Node). */
export async function isAuthenticated(): Promise<boolean> {
  const store = await cookies();
  return verifyToken(store.get(COOKIE_NAME)?.value);
}

export async function setSessionCookie(): Promise<void> {
  const store = await cookies();
  store.set(COOKIE_NAME, await signToken(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_DAYS * 24 * 60 * 60,
  });
}

export async function clearSessionCookie(): Promise<void> {
  const store = await cookies();
  store.delete(COOKIE_NAME);
}

export function checkPassword(input: string): boolean {
  const expected = process.env.APP_PASSWORD;
  if (!expected) throw new Error("APP_PASSWORD manquant.");
  if (input.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < input.length; i++)
    diff |= input.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}
