"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { checkPassword, setSessionCookie, clearSessionCookie } from "./auth";
import { CAMPAIGNS, CAMPAIGN_COOKIE } from "./constants";

const VALID_CAMPAIGN_KEYS = new Set<string>(CAMPAIGNS.map((c) => c.key));

export type LoginState = { error?: string };

export async function loginAction(
  _prev: LoginState,
  formData: FormData
): Promise<LoginState> {
  const password = String(formData.get("password") ?? "");
  const from = String(formData.get("from") ?? "/");
  if (!checkPassword(password)) {
    return { error: "Mot de passe incorrect." };
  }
  await setSessionCookie();
  redirect(from.startsWith("/") ? from : "/");
}

export async function logoutAction(): Promise<void> {
  await clearSessionCookie();
  redirect("/login");
}

export async function setCampaignAction(formData: FormData): Promise<void> {
  const key = String(formData.get("campaign") ?? "");
  if (!VALID_CAMPAIGN_KEYS.has(key)) return;
  const store = await cookies();
  store.set(CAMPAIGN_COOKIE, key, {
    httpOnly: false, // lecture client utile pour l'UX
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 90, // 90 jours
  });
}
