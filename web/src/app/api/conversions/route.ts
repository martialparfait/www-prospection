import "server-only";
import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Endpoint appelé par wellmap.org au moment d'un signup (hook user_register).
 *
 * Payload attendu :
 *   {
 *     "draft_id": "uuid",         // = utm_content reçu dans l'URL de signup
 *     "email": "user@example.com",
 *     "registered_at": "2026-06-08T10:34:11Z",
 *     "campaign": "metro_fitness_2026",    // optionnel — sinon déduit de email_sends
 *     "subject_variant": "A"               // optionnel — sinon déduit
 *   }
 *
 * Auth : header `X-WWW-Token` == env WWW_CONVERSIONS_TOKEN (timing-safe).
 *
 * Effet :
 *   1. Insère une ligne dans email_conversions (audit, idempotent par draft_id+email)
 *   2. Met à jour email_sends.registered/registered_at/registered_email pour la
 *      ligne dont draft_id matche
 */

type ConversionPayload = {
  draft_id?: string;
  email?: string;
  registered_at?: string;
  campaign?: string | null;
  subject_variant?: string | null;
};

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function timingSafeEq(a: string, b: string): boolean {
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) return false;
  return crypto.timingSafeEqual(ab, bb);
}

export async function POST(req: NextRequest) {
  const expected = process.env.WWW_CONVERSIONS_TOKEN;
  if (!expected) {
    return NextResponse.json(
      { ok: false, error: "Server not configured (missing WWW_CONVERSIONS_TOKEN)" },
      { status: 503 },
    );
  }
  const provided = req.headers.get("x-www-token") ?? "";
  if (!provided || !timingSafeEq(provided, expected)) {
    return new NextResponse("Unauthorized", { status: 401 });
  }

  let body: ConversionPayload;
  try {
    body = (await req.json()) as ConversionPayload;
  } catch {
    return new NextResponse("Invalid JSON", { status: 400 });
  }

  const draftId = (body.draft_id ?? "").trim();
  const email = (body.email ?? "").trim().toLowerCase();
  const registeredAt = body.registered_at ?? new Date().toISOString();

  if (!draftId || !UUID_RE.test(draftId)) {
    return NextResponse.json({ ok: false, error: "draft_id missing or not a UUID" }, { status: 400 });
  }
  if (!email || !email.includes("@")) {
    return NextResponse.json({ ok: false, error: "email missing or invalid" }, { status: 400 });
  }

  // 1. Lookup email_sends pour cette draft (preuve qu'on a bien envoyé)
  const { data: send } = await supabase
    .from("email_sends")
    .select("id,campaign,subject_variant,recipient_email")
    .eq("draft_id", draftId)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  const campaign = body.campaign ?? send?.campaign ?? null;
  const subjectVariant = body.subject_variant ?? send?.subject_variant ?? null;

  // 2. Audit row (idempotent grâce à ON CONFLICT virtuel : on accepte les doublons
  //    — chaque appel reste tracé, le dédoublonnage se fait à la lecture)
  const { error: convErr } = await supabase.from("email_conversions").insert({
    draft_id: draftId,
    send_id: send?.id ?? null,
    email,
    campaign,
    subject_variant: subjectVariant,
    registered_at: registeredAt,
    raw_payload: body as unknown as Record<string, unknown>,
  });
  if (convErr) {
    console.error("Failed to insert email_conversion:", convErr);
    return NextResponse.json({ ok: false, error: "DB insert failed" }, { status: 500 });
  }

  // 3. Si on a une ligne email_sends correspondante, on marque la conversion.
  //    On n'écrase pas une conversion plus ancienne (le 1er signup gagne).
  if (send?.id) {
    const { error: updErr } = await supabase
      .from("email_sends")
      .update({
        registered: true,
        registered_at: registeredAt,
        registered_email: email,
      })
      .eq("id", send.id)
      .is("registered_at", null);
    if (updErr) {
      console.error("Failed to update email_sends.registered:", updErr);
    }
  }

  return NextResponse.json({
    ok: true,
    matched_send: Boolean(send?.id),
  });
}

// Healthcheck — wellmap.org peut le ping pour vérifier qu'on est UP.
export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "WWW Prospection — conversions endpoint",
    auth_configured: Boolean(process.env.WWW_CONVERSIONS_TOKEN),
  });
}
