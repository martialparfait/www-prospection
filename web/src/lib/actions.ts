"use server";

import { redirect } from "next/navigation";
import { checkPassword, setSessionCookie, clearSessionCookie } from "./auth";

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
