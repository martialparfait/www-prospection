"""
World Wellness Weekend — Envoi des drafts personnalisés via SendGrid.

Pour chaque draft (filtré par status), envoie l'email via SendGrid avec :
  - Click tracking ACTIVÉ (pour stats actionables)
  - Open tracking DÉSACTIVÉ (déclenche les filtres spam, données peu fiables 2026)
  - Custom args (draft_id, campaign, segment, country, subject_variant) → reviennent
    dans les webhook events pour le matching côté `email_sends`
  - List-Unsubscribe headers RFC 8058 (one-click) si subscription tracking ON
  - Insertion dans `email_sends` (provider_msg_id pour le matching webhook)
  - Update du draft.status → 'sent'

Variables .env (à compléter avant le 1er envoi) :
    SENDGRID_API_KEY            → ta clé API SendGrid
    SENDGRID_FROM_EMAIL         → ex. jean-guy@world-wellness-weekend.org
    SENDGRID_FROM_NAME          → ex. "Jean-Guy de Gabriac"
    SENDGRID_REPLY_TO           → ex. jean-guy@world-wellness-weekend.org (idem from)
    SENDGRID_UNSUB_GROUP_ID     → (optionnel) id du groupe Unsubscribe SendGrid

Prérequis IMPÉRATIFS côté SendGrid (sinon deliverability catastrophique) :
    1. Sender Authentication → Authenticate Your Domain → DNS CNAME records publiés
    2. Single Sender Verification de l'adresse Jean-Guy
    3. Event Webhook configuré → URL https://www-prospection.vercel.app/api/sendgrid/webhook
    4. Unsubscribe Group créé (recommandé)
    5. Dedicated IP (optionnel mais recommandé pour 1500+ envois)

Usage :
    python3 send_drafts.py --test you@yourdomain.com    # envoie 1 mail au test
    python3 send_drafts.py --status approved --limit 1  # 1 envoi réel pour QC
    python3 send_drafts.py --status approved            # tous les approuvés
    python3 send_drafts.py --status draft --dry-run     # liste les drafts à envoyer
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client

# Import paresseux de sendgrid (pour permettre --dry-run sans le package)

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")
SG_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")
FROM_NAME = os.environ.get("SENDGRID_FROM_NAME", "Jean-Guy de Gabriac")
REPLY_TO = os.environ.get("SENDGRID_REPLY_TO") or FROM_EMAIL
_RAW_UNSUB = os.environ.get("SENDGRID_UNSUB_GROUP_ID", "").strip()
try:
    UNSUB_GROUP_ID = int(_RAW_UNSUB) if _RAW_UNSUB else None
except ValueError:
    print(
        f"⚠️  SENDGRID_UNSUB_GROUP_ID='{_RAW_UNSUB}' n'est pas un entier — "
        "l'ASM SendGrid sera désactivée (List-Unsubscribe sera quand même injecté via mail body).",
        file=sys.stderr,
    )
    UNSUB_GROUP_ID = None

DEFAULT_CAMPAIGN = "metro_fitness_2026"
THROTTLE_SECONDS = 0.5  # ~120 emails/min, sous les limites SendGrid


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def check_config(dry_run: bool):
    missing = []
    if not SUPABASE_URL or not SUPABASE_KEY:
        missing.append("SUPABASE_URL/SUPABASE_SECRET_KEY")
    if not dry_run:
        if not SG_API_KEY:
            missing.append("SENDGRID_API_KEY")
        if not FROM_EMAIL:
            missing.append("SENDGRID_FROM_EMAIL")
    if missing:
        sys.exit(f"❌ Variables .env manquantes : {', '.join(missing)}")


def build_sendgrid_mail(draft: dict, override_to: Optional[str] = None):
    """Construit l'objet Mail SendGrid à partir d'un draft."""
    from sendgrid.helpers.mail import (
        Mail, Email, To, ReplyTo, Subject, HtmlContent, PlainTextContent,
        CustomArg, TrackingSettings, ClickTracking, OpenTracking,
        SubscriptionTracking,
    )

    recipient = override_to or draft["recipient_email"]
    mail = Mail(
        from_email=Email(FROM_EMAIL, FROM_NAME),
        to_emails=To(recipient),
        subject=Subject(draft["subject"]),
        html_content=HtmlContent(draft["body_html"]),
        plain_text_content=PlainTextContent(draft["body_plain"]),
    )
    if REPLY_TO and REPLY_TO != FROM_EMAIL:
        mail.reply_to = ReplyTo(REPLY_TO)

    # Custom args — reviennent dans les webhook events
    mail.add_custom_arg(CustomArg("draft_id", str(draft["id"])))
    mail.add_custom_arg(CustomArg("campaign", str(draft["campaign"])))
    mail.add_custom_arg(CustomArg("segment", str(draft["segment"])))
    if draft.get("country"):
        mail.add_custom_arg(CustomArg("country", str(draft["country"])))
    if draft.get("haiku_subject_variant"):
        mail.add_custom_arg(CustomArg("subject_variant", str(draft["haiku_subject_variant"])))
    if draft.get("establishment_id"):
        mail.add_custom_arg(CustomArg("establishment_id", str(draft["establishment_id"])))

    # Tracking : click ON, open OFF (politique choisie)
    tracking = TrackingSettings()
    tracking.click_tracking = ClickTracking(enable=True, enable_text=False)
    tracking.open_tracking = OpenTracking(enable=False)
    mail.tracking_settings = tracking

    # Asm group (si défini) → SendGrid gère l'opt-out group automatiquement
    # et injecte le header List-Unsubscribe + List-Unsubscribe-Post (RFC 8058).
    if UNSUB_GROUP_ID:
        from sendgrid.helpers.mail import Asm, GroupId
        mail.asm = Asm(group_id=GroupId(UNSUB_GROUP_ID))

    return mail


def insert_send_row(sb, draft: dict, provider_msg_id: Optional[str]):
    payload = {
        "draft_id": draft["id"],
        "contact_id": draft.get("contact_id"),
        "establishment_id": draft["establishment_id"],
        "recipient_email": draft["recipient_email"],
        "campaign": draft["campaign"],
        "segment": draft["segment"],
        "country": draft.get("country"),
        "subject_variant": draft.get("haiku_subject_variant"),
        "provider_msg_id": provider_msg_id,
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    sb.table("email_sends").insert(payload).execute()


def mark_sent(sb, draft_id: str):
    sb.table("email_drafts").update({"status": "sent"}).eq("id", draft_id).execute()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def fetch_drafts(sb, status: str, limit: int, campaign: str = DEFAULT_CAMPAIGN) -> list[dict]:
    """Charge les drafts à envoyer, avec country de l'établissement (pour custom args)."""
    PAGE = 500
    out: list[dict] = []
    offset = 0
    while True:
        q = (sb.table("email_drafts")
             .select("id,contact_id,establishment_id,campaign,segment,recipient_email,subject,body_html,body_plain,haiku_subject_variant,status,establishments(country)")
             .eq("status", status)
             .eq("campaign", campaign)
             .order("generated_at")
             .range(offset, offset + PAGE - 1))
        rows = q.execute().data
        if not rows:
            break
        for r in rows:
            r["country"] = (r.get("establishments") or {}).get("country")
        out.extend(rows)
        if limit and len(out) >= limit:
            return out[:limit]
        if len(rows) < PAGE:
            break
        offset += PAGE
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--status", choices=["draft", "approved"], help="Envoyer tous les drafts du statut donné")
    g.add_argument("--test", help="Envoie 1 seul email au destinataire fourni (avec le 1er draft dispo)")
    ap.add_argument("--limit", type=int, default=0, help="Limite d'envois (sécurité)")
    ap.add_argument("--campaign", default=DEFAULT_CAMPAIGN, help="Campagne à envoyer (défaut: metro_fitness_2026)")
    ap.add_argument("--dry-run", action="store_true", help="Liste les drafts sans rien envoyer")
    args = ap.parse_args()

    check_config(args.dry_run)
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    if args.test:
        drafts = fetch_drafts(sb, "draft", 1, args.campaign)
        if not drafts:
            sys.exit("❌ Aucun draft à utiliser pour le test")
        drafts[0]["_override_to"] = args.test
    else:
        drafts = fetch_drafts(sb, args.status, args.limit or 0, args.campaign)

    print(f"📤 {len(drafts)} email(s) à envoyer"
          + (f" → override_to={args.test}" if args.test else "")
          + (" [DRY-RUN]" if args.dry_run else ""))

    if args.dry_run:
        for d in drafts:
            print(f"   • {d['recipient_email']:40} | {d['subject']}")
        return

    # Lazy import du SDK SendGrid
    import sendgrid

    sg = sendgrid.SendGridAPIClient(api_key=SG_API_KEY)

    sent, failed = 0, 0
    for i, draft in enumerate(drafts, 1):
        override = draft.pop("_override_to", None)
        target = override or draft["recipient_email"]
        print(f"[{i}/{len(drafts)}] {draft['country'] or '??'} | {target[:40]:40} | {draft['subject'][:50]}",
              flush=True)
        try:
            mail = build_sendgrid_mail(draft, override_to=override)
            resp = sg.client.mail.send.post(request_body=mail.get())
            if 200 <= resp.status_code < 300:
                msg_id = resp.headers.get("X-Message-Id") or resp.headers.get("x-message-id")
                insert_send_row(sb, draft, msg_id)
                if not override:
                    mark_sent(sb, draft["id"])
                print(f"   ✅ sent (msg_id={msg_id})")
                sent += 1
            else:
                print(f"   ❌ HTTP {resp.status_code} : {resp.body[:160]}", file=sys.stderr)
                failed += 1
        except Exception as e:
            import traceback
            print(f"   ❌ {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            failed += 1
        time.sleep(THROTTLE_SECONDS)

    print(f"\n===== RÉCAP =====\n  envoyés : {sent}\n  échecs  : {failed}")


if __name__ == "__main__":
    main()
