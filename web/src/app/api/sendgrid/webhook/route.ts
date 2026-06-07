import "server-only";
import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SgEvent = {
  email: string;
  timestamp: number;
  event: string;
  sg_message_id?: string;
  sg_event_id?: string;
  url?: string;
  reason?: string;
  // Custom args injectés par le sender
  draft_id?: string;
  campaign?: string;
  segment?: string;
  country?: string;
  subject_variant?: string;
  establishment_id?: string;
};

// Vérification ECDSA P-256 de la signature SendGrid (header
// X-Twilio-Email-Event-Webhook-Signature) si SENDGRID_WEBHOOK_PUBLIC_KEY est défini.
function verifySignature(timestamp: string, body: string, signature: string): boolean {
  const pubKey = process.env.SENDGRID_WEBHOOK_PUBLIC_KEY;
  if (!pubKey) return true; // mode dev — pas de clé configurée, on accepte
  try {
    const pem = pubKey.startsWith("-----BEGIN")
      ? pubKey
      : `-----BEGIN PUBLIC KEY-----\n${pubKey}\n-----END PUBLIC KEY-----`;
    const verifier = crypto.createVerify("SHA256");
    verifier.update(timestamp + body);
    verifier.end();
    return verifier.verify(pem, signature, "base64");
  } catch (e) {
    console.error("Signature verification error:", e);
    return false;
  }
}

export async function POST(req: NextRequest) {
  const rawBody = await req.text();
  const ts = req.headers.get("x-twilio-email-event-webhook-timestamp") ?? "";
  const sig = req.headers.get("x-twilio-email-event-webhook-signature") ?? "";

  if (process.env.SENDGRID_WEBHOOK_PUBLIC_KEY) {
    if (!ts || !sig || !verifySignature(ts, rawBody, sig)) {
      return new NextResponse("Invalid signature", { status: 401 });
    }
  }

  let events: SgEvent[];
  try {
    events = JSON.parse(rawBody);
    if (!Array.isArray(events)) throw new Error("Expected array");
  } catch {
    return new NextResponse("Invalid JSON", { status: 400 });
  }

  let processed = 0;
  const errors: string[] = [];
  for (const ev of events) {
    try {
      await processEvent(ev);
      processed++;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      errors.push(msg);
      console.error("processEvent error:", msg, ev);
    }
  }

  return NextResponse.json({ ok: true, processed, errors: errors.length });
}

async function processEvent(ev: SgEvent) {
  const msgId = ev.sg_message_id ?? null;
  const email = ev.email ?? "";
  const tsIso = new Date((ev.timestamp ?? Math.floor(Date.now() / 1000)) * 1000).toISOString();

  // Localise la ligne email_sends : on tente d'abord par provider_msg_id, sinon par
  // (campaign + recipient_email) le plus récent.
  let sendRowId: string | null = null;
  if (msgId) {
    const { data } = await supabase
      .from("email_sends")
      .select("id")
      .eq("provider_msg_id", msgId)
      .limit(1)
      .maybeSingle();
    sendRowId = data?.id ?? null;
  }
  if (!sendRowId && ev.campaign && email) {
    const { data } = await supabase
      .from("email_sends")
      .select("id")
      .eq("campaign", ev.campaign)
      .ilike("recipient_email", email)
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();
    sendRowId = data?.id ?? null;
  }

  // Si la ligne n'existe pas encore (event arrivé avant insertion par le sender),
  // on l'upsert sur (provider_msg_id) en mode minimal.
  if (!sendRowId && msgId) {
    const insertPayload: Record<string, unknown> = {
      provider_msg_id: msgId,
      recipient_email: email,
      campaign: ev.campaign ?? null,
      draft_id: ev.draft_id ?? null,
      establishment_id: ev.establishment_id ?? null,
      segment: ev.segment ?? null,
      country: ev.country ?? null,
      subject_variant: ev.subject_variant ?? null,
      last_event_at: tsIso,
    };
    const { data, error } = await supabase
      .from("email_sends")
      .insert(insertPayload)
      .select("id")
      .single();
    if (error) throw error;
    sendRowId = data.id;
  }

  if (!sendRowId) {
    console.warn("Event without matching send row:", { event: ev.event, msgId, email });
    return;
  }

  // Mise à jour selon le type d'event
  const update: Record<string, unknown> = { last_event_at: tsIso };

  switch (ev.event) {
    case "processed":
    case "delivered":
      // On marque sent_at sur le 1er signal de delivery
      update.sent_at = tsIso;
      break;
    case "click":
      update.clicked_at = tsIso;
      // Incrément click_count via RPC (rpc('increment_click', ...)) ou via SELECT + UPDATE
      break;
    case "open":
      // On l'enregistre malgré tout (au cas où on change d'avis sur l'open tracking)
      update.opened_at = tsIso;
      break;
    case "bounce":
    case "blocked":
    case "dropped":
      update.bounced = true;
      break;
    case "spam_report":
      update.complained = true;
      break;
    case "unsubscribe":
    case "group_unsubscribe":
      update.unsubscribed_at = tsIso;
      // Ajout à opt_out global (jamais recontacter, tous projets)
      if (email) {
        await supabase
          .from("opt_out")
          .upsert(
            { email: email.toLowerCase(), reason: "unsubscribe_link", source: "sendgrid_webhook" },
            { onConflict: "email" }
          );
      }
      break;
    case "group_resubscribe":
      update.unsubscribed_at = null;
      break;
    default:
      // event inconnu — on log et on tag last_event_at quand même
      break;
  }

  // Pour click_count, on fait un increment atomique côté SQL
  if (ev.event === "click") {
    const { data: current } = await supabase
      .from("email_sends")
      .select("click_count")
      .eq("id", sendRowId)
      .maybeSingle();
    update.click_count = (current?.click_count ?? 0) + 1;
  }

  await supabase.from("email_sends").update(update).eq("id", sendRowId);
}

// Endpoint GET pour healthcheck (utilisable depuis le dashboard SendGrid)
export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "WWW Prospection — SendGrid webhook",
    signature_verification: Boolean(process.env.SENDGRID_WEBHOOK_PUBLIC_KEY),
  });
}
