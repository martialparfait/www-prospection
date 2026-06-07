"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { checkPassword, setSessionCookie, clearSessionCookie } from "./auth";
import { CAMPAIGNS, CAMPAIGN_COOKIE, ACTIVE_CAMPAIGN } from "./constants";
import { supabase } from "./supabase";

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

// -------------------------------------------------------------------------- //
// Draft review actions
// -------------------------------------------------------------------------- //

const REVIEWER = "web-ui"; // placeholder — pas d'auth multi-user pour l'instant

export async function approveDraftAction(formData: FormData): Promise<void> {
  const id = String(formData.get("id") ?? "");
  if (!id) return;
  await supabase
    .from("email_drafts")
    .update({
      status: "approved",
      reviewed_at: new Date().toISOString(),
      reviewed_by: REVIEWER,
    })
    .eq("id", id)
    .eq("status", "draft"); // ne pas écraser un approved/rejected/sent existant
  revalidatePath(`/drafts/${id}`);
  revalidatePath("/drafts");
}

export async function rejectDraftAction(formData: FormData): Promise<void> {
  const id = String(formData.get("id") ?? "");
  const notes = String(formData.get("notes") ?? "").trim() || null;
  if (!id) return;
  await supabase
    .from("email_drafts")
    .update({
      status: "rejected",
      reviewed_at: new Date().toISOString(),
      reviewed_by: REVIEWER,
      notes,
    })
    .eq("id", id)
    .eq("status", "draft");
  revalidatePath(`/drafts/${id}`);
  revalidatePath("/drafts");
}

export async function viewRandomDraftAction(formData: FormData): Promise<void> {
  // Sélectionne un draft au hasard parmi ceux qui matchent les filtres et
  // redirige vers son détail. Sert au QA sample avant le bulk-approve.
  const campaign = String(formData.get("campaign") ?? ACTIVE_CAMPAIGN);
  const country = String(formData.get("country") ?? "").trim() || null;
  const segment = String(formData.get("segment") ?? "").trim() || null;
  const status = String(formData.get("status") ?? "draft").trim();
  if (!VALID_CAMPAIGN_KEYS.has(campaign)) return;

  let query = supabase
    .from("email_drafts")
    .select("id,establishments!inner(country,batch)")
    .eq("campaign", campaign)
    .eq("status", status)
    .eq("establishments.batch", campaign);
  if (country) query = query.eq("establishments.country", country);
  if (segment) query = query.eq("segment", segment);

  // PostgREST n'a pas de RANDOM() — on charge max 1000 ids puis on en pick 1
  const { data } = await query.limit(1000);
  const rows = (data ?? []) as { id: string }[];
  if (rows.length === 0) {
    redirect("/drafts?status=" + status);
  }
  const pick = rows[Math.floor(Math.random() * rows.length)];
  redirect(`/drafts/${pick.id}?from=qa`);
}

export async function bulkApproveDraftsAction(formData: FormData): Promise<void> {
  // Approuve TOUS les drafts encore en status="draft" qui matchent les filtres
  // courants (campaign + country/segment optionnels). On reste sur la campagne
  // active pour éviter les approbations massives accidentelles cross-campaign.
  const campaign = String(formData.get("campaign") ?? ACTIVE_CAMPAIGN);
  const country = String(formData.get("country") ?? "").trim() || null;
  const segment = String(formData.get("segment") ?? "").trim() || null;
  if (!VALID_CAMPAIGN_KEYS.has(campaign)) return;

  // On ne peut pas filtrer côté Supabase sur establishments.country dans un UPDATE
  // (PostgREST ne supporte pas le join sur UPDATE). On fait donc en 2 temps :
  //   1. SELECT des ids à approuver
  //   2. UPDATE par batch d'ids
  let query = supabase
    .from("email_drafts")
    .select("id,establishments!inner(country)")
    .eq("campaign", campaign)
    .eq("status", "draft")
    .eq("establishments.batch", campaign);
  if (country) query = query.eq("establishments.country", country);
  if (segment) query = query.eq("segment", segment);

  const PAGE = 1000;
  const ids: string[] = [];
  let offset = 0;
  while (true) {
    const { data, error } = await query.range(offset, offset + PAGE - 1);
    if (error) throw error;
    const rows = (data ?? []) as { id: string }[];
    ids.push(...rows.map((r) => r.id));
    if (rows.length < PAGE) break;
    offset += PAGE;
  }

  // Update par chunks de 500 (limite raisonnable pour un IN clause)
  const reviewedAt = new Date().toISOString();
  const CHUNK = 500;
  for (let i = 0; i < ids.length; i += CHUNK) {
    const chunk = ids.slice(i, i + CHUNK);
    await supabase
      .from("email_drafts")
      .update({
        status: "approved",
        reviewed_at: reviewedAt,
        reviewed_by: REVIEWER + "-bulk",
      })
      .in("id", chunk);
  }
  revalidatePath("/drafts");
  revalidatePath("/stats");
}
