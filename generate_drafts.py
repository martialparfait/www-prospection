"""
World Wellness Weekend — Génération de drafts d'email personnalisés via Claude Haiku 4.5.

Pour chaque destinataire (contact nominatif OU boîte générique sur establishment) :
  1. Construit l'input Haiku à partir des données Supabase
  2. Appelle Claude Haiku 4.5 (tool_use pour structured output)
  3. Valide anti-hallucination (banned words, placeholders leak, peer chain match…)
  4. Rend le HTML final en injectant les variables dans docs/email_template_render.html
  5. Stocke le draft dans `email_drafts` (status=draft) pour review client

Variables .env :
    SUPABASE_URL, SUPABASE_SECRET_KEY
    CLAUDE_API_KEY (ou ANTHROPIC_API_KEY)

Usage :
    python3 generate_drafts.py --sample 10
    python3 generate_drafts.py --sample 10 --country US
    python3 generate_drafts.py --all
    python3 generate_drafts.py --regenerate-rejected
"""

import argparse
import json
import os
import random
import re
import sys
import time
import uuid
from html import escape
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

from anthropic import Anthropic
from dotenv import load_dotenv
from supabase import create_client

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")
CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_KEY:
    sys.exit("❌ Aucune clé Anthropic dans .env (ANTHROPIC_API_KEY ou CLAUDE_API_KEY).")

HAIKU_MODEL = "claude-haiku-4-5-20251001"
CAMPAIGN = "metro_fitness_2026"
RENDER_TEMPLATE_PATH = ROOT / "docs" / "email_template_render.html"

# Base de la CTA — les UTMs sont ajoutés par draft (utm_content = draft_id pour
# le matching côté wellmap.org → /api/conversions lors d'un signup).
CTA_BASE_URL = "https://map.world-wellness-weekend.org/my-account/login/"
PRIVACY_URL = "https://world-wellness-weekend.org/privacy/"


def build_cta_url(draft_id: str, campaign: str, subject_variant: Optional[str]) -> str:
    """URL CTA tracée — utm_content=draft_id sert de pivot pour la conversion site."""
    params = {
        "utm_source": "cold_email",
        "utm_medium": "email",
        "utm_campaign": campaign,
        "utm_content": draft_id,
    }
    if subject_variant:
        params["utm_term"] = subject_variant
    return f"{CTA_BASE_URL}?{urlencode(params)}"

# Catégories internes : enum → venue_noun + format suggéré.
CATEGORY_PROFILES = {
    "reformer_pilates": {"venue_noun": "studio",
                         "category_format": "a 30-minute beginner reformer demo open to the curious"},
    "yoga_pilates":     {"venue_noun": "studio",
                         "category_format": "a 45-minute Sunrise Flow or a candlelit Yin session open to the curious"},
    "boutique_fitness": {"venue_noun": "studio",
                         "category_format": "a 30-minute signature class open to non-members"},
    "barre":            {"venue_noun": "studio",
                         "category_format": "a 45-minute signature barre class open to non-members"},
    "cycling":          {"venue_noun": "studio",
                         "category_format": "a 45-minute rhythm ride open to non-members"},
    "crossfit":         {"venue_noun": "box",
                         "category_format": "an open WOD scaled for all levels"},
    "boxing_martial":   {"venue_noun": "studio",
                         "category_format": "a 30-minute intro class — wraps provided, no commitment"},
    "hotel_wellness":   {"venue_noun": "venue",
                         "category_format": "a guided pool and sauna ritual for local non-residents"},
    "gym":              {"venue_noun": "club",
                         "category_format": "a 45-minute HIIT or Functional taster session open to non-members"},
    "other_fitness":    {"venue_noun": "studio",
                         "category_format": "a 30-minute taster session open to non-members"},
}


def infer_category_from_name(name: str, db_category: Optional[str]) -> str:
    """Devine la catégorie 'fine' depuis le nom de l'établissement.
    Override la catégorie DB (souvent juste 'fitness') quand le nom est explicite."""
    n = (name or "").lower()
    # Ordre = priorité (plus spécifique d'abord)
    if "reformer" in n:
        return "reformer_pilates"
    if "pilates" in n:
        return "reformer_pilates"
    if "yoga" in n or "ashtanga" in n or "vinyasa" in n or "bikram" in n:
        return "yoga_pilates"
    if "barre" in n:
        return "barre"
    if "soulcycle" in n or "cyclebar" in n or "rumble" in n and "cycle" in n or "spin" in n:
        return "cycling"
    if "crossfit" in n:
        return "crossfit"
    if "boxing" in n or "muay thai" in n or "kickbox" in n or "mma" in n or "jiu-jitsu" in n or "jiujitsu" in n or "karate" in n or "judo" in n or "taekwondo" in n or "dojo" in n:
        return "boxing_martial"
    if any(h in n for h in ("hotel", "resort", "marriott", "hilton", "hyatt", "sofitel", "ihg", "intercontinental", "westin", "ritz", "four seasons", "shangri-la", "kimpton")):
        return "hotel_wellness"
    # Mid-range / boutique branded studios (sans label clair → 'boutique')
    if any(h in n for h in ("studio", "boutique", "loft")):
        return "boutique_fitness"
    # Fallback : si le DB dit fitness/gym → gym ; sinon other
    if db_category in ("fitness", "gym"):
        return "gym"
    return "other_fitness"

PEER_CHAIN_BY_COUNTRY = {
    "US": "Equinox-affiliated studios and CorePower Yoga locations",
    "GB": "120+ David Lloyd clubs across the UK",
    "AU": "Across Australia, Fitness First clubs and Anytime Fitness studios",
}
SHORT_PEER_BY_COUNTRY = {"US": "CorePower", "GB": "David Lloyd", "AU": "Fitness First"}

# Détection de boîtes génériques (local-part)
GENERIC_LOCALS = {
    "info", "contact", "hello", "hi", "admin", "support", "booking", "bookings",
    "team", "office", "reception", "frontdesk", "studio", "help", "sales",
    "namaste", "yoga", "members", "membership", "enquiries", "inquiries",
    "mail", "general", "welcome", "schedule", "classes", "wellness", "fitness",
    "membership", "memberservices", "concierge",
}

# Mots / patterns BANNIS dans la sortie Haiku
BANNED_PHRASES = [
    "renowned", "award-winning", "famous", "iconic", "leading", "well-known",
    "personalized", "tailored", "leverage", "synergy", "unlock", "elevate",
    "unparalleled", "best-in-class", "world-class", "cutting-edge", "game-changer", "disrupt",
    "i hope this", "i came across", "i was impressed", "quick question", "just checking in",
    "don't miss out", "limited time", "act now", "last chance", "exclusive offer",
    "your team of", "your beautiful space", "since 20", "founded in",
]


# --------------------------------------------------------------------------- #
# Haiku
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """You are the email-personalization engine for World Wellness Weekend (WWW).
Generate ONE short, warm, professional B2B invitation email per input record.
Output ONLY via the `emit_email_draft` tool — no preamble, no explanation.

# ABOUT WWW — IMMUTABLE FACTS (never embellish)
- Dates: September 18-19-20, 2026. 10th edition.
- 15,000 venues, 190 countries.
- Over 20 million media views in 2025.
- Free for participating venues. No fee. No commission.
- Sender: Jean-Guy de Gabriac, Founder. International non-profit association.
- Single CTA URL (added downstream as a button, NOT by you): https://map.world-wellness-weekend.org/my-account/login/
- Core human pitch: many people hesitate to join — let them experience the venue without pressure during one weekend.

# YOUR OUTPUT — 3 body paragraphs only (no CTA, no closer, no signature)
[0] GREETING line (one short line):
   - If decision_maker_first_name is provided AND is_generic_inbox is false: "Hi {first_name},"
   - Otherwise: "Hi team at {establishment_name},"

[1] HOOK + SOCIAL PROOF (one paragraph, 2 sentences):
   Sentence A — HOOK:
     "Saw {establishment_name} in {city} — exactly the kind of {venue_noun} we built the 10th World Wellness Weekend (Sept 18-20, 2026) for."
     (If establishment_city is null/empty: drop " in {city}" entirely; never write "in null".)
     ({venue_noun} = "studio"/"gym"/"club"/"venue" matching the category.)
   Sentence B — PROOF:
     "{peer_chain_hint} are joining 15,000 venues in 190 countries — over 20 million media views in 2025 — to host one free class that weekend, no fee, no commission."
     (Use EXACTLY the provided peer_chain_hint. Do not substitute, shorten, or invent peers.)

[2] FORMAT (one short paragraph, 1 sentence):
   Template: "For a {venue_noun} like yours, {category_format} would slot in perfectly: people who hesitate to commit get to try without pressure."
   Optional weave: if decision_maker_role is provided AND fits as peer-talk, you may rephrase: "As {role}, you know how a single open session converts people who walked past for months — {category_format} fits the format perfectly."

# SUBJECT
Pick ONE pattern based on target_subject_pattern provided:
- A: "A free September weekend for {establishment_name}?"
- B: "Idea for {establishment_name}"
- C: "Why {short_peer_name} joined — and {establishment_name}?"
- D: "{city} fitness on the wellness world map"   (only if city is non-null)
- E: "A small ask for {establishment_name}"

Subject rules: 4-8 words, ≤ 60 characters. No ALL CAPS. No exclamation marks. No emojis. NEVER include the recipient's first name.

# HARD INTERDICTIONS — VIOLATIONS WILL FAIL VALIDATION
1. NEVER invent facts about the establishment ("renowned", "award-winning", "since YYYY", "famous", "iconic", "leading", "well-known", "your team of X", "your beautiful space").
2. NEVER invent a person's name. If first_name is null/empty, use "Hi team at {establishment_name},".
3. NEVER mention a role if decision_maker_role is null.
4. NEVER mention a peer chain other than the EXACT peer_chain_hint provided. Do not substitute "Equinox" for "David Lloyd", etc.
5. NEVER mention a city if establishment_city is null.
6. NEVER use these words/phrases: personalized, tailored, leverage, synergy, unlock, elevate, unparalleled, best-in-class, world-class, cutting-edge, game-changer, disrupt, "I hope this finds you well", "I came across", "I was impressed", "Quick question", "Just checking in", "Don't miss out", "Limited time", "Act now", "Last chance".
7. NEVER use exclamation marks. NEVER ALL CAPS. NEVER emojis.
8. NEVER include any URL — the CTA is static, added downstream.
9. NEVER add a P.S., postscript, sign-off, "Warm regards", "Best", or any closing. body_paragraphs ends after the format paragraph.
10. NEVER output any placeholder artifact: no "{", "}", "null", "None", "undefined", "[redacted]".

Tone: warm peer-to-peer, never marketer, never AI. Concise. Professional."""


EMIT_TOOL = {
    "name": "emit_email_draft",
    "description": "Emit the personalized email draft. Always call this tool exactly once.",
    "input_schema": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Email subject line. 4-8 words. ≤60 chars. No ALL CAPS, no exclamation, no emoji, no first name.",
                "maxLength": 60,
            },
            "body_paragraphs": {
                "type": "array",
                "description": "Exactly 3 strings: [0]=greeting, [1]=hook+proof, [2]=format suggestion.",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 3,
            },
        },
        "required": ["subject", "body_paragraphs"],
    },
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def is_generic_email(email: str) -> bool:
    if not email or "@" not in email:
        return True
    local = email.split("@")[0].lower()
    token = re.split(r"[._\-+]", local)[0]
    return local in GENERIC_LOCALS or token in GENERIC_LOCALS


def pick_subject_pattern(is_generic: bool, has_city: bool, has_role: bool) -> str:
    if not is_generic and has_city:
        return "A"
    if not is_generic and not has_city:
        return "B"
    if is_generic and has_city:
        return "D"
    return "E"


def build_haiku_input(row: dict) -> dict:
    """row a {contact: {...} or None, establishment: {...}, recipient_email, segment}."""
    contact = row.get("contact") or {}
    estab = row["establishment"]
    country = (estab.get("country") or "").upper()[:2]
    if country not in PEER_CHAIN_BY_COUNTRY:
        raise ValueError(f"Country {country!r} non supporté")

    first_name = (contact.get("first_name") or "").strip() or None
    role = (contact.get("role") or "").strip() or None
    is_generic = row["segment"] == "B_generic_inbox" or not first_name or is_generic_email(row["recipient_email"])

    cat_enum = infer_category_from_name(estab["name"], (estab.get("category") or "").lower())
    cat_info = CATEGORY_PROFILES[cat_enum]

    has_city = bool((estab.get("city") or "").strip())

    return {
        "decision_maker_first_name": first_name,
        "decision_maker_role": role,
        "establishment_name": estab["name"].strip(),
        "establishment_city": (estab.get("city") or "").strip() or None,
        "establishment_country": country,
        "establishment_category_enum": cat_enum,
        "venue_noun": cat_info["venue_noun"],
        "category_format": cat_info["category_format"],
        "peer_chain_hint": PEER_CHAIN_BY_COUNTRY[country],
        "short_peer_name": SHORT_PEER_BY_COUNTRY[country],
        "is_generic_inbox": is_generic,
        "target_subject_pattern": pick_subject_pattern(is_generic, has_city, bool(role)),
    }


def call_haiku(client: Anthropic, haiku_input: dict, retries: int = 2) -> tuple[str, list[str]]:
    """Renvoie (subject, body_paragraphs)."""
    user_msg = (
        "Generate the email draft for this record. Return ONLY the tool call.\n\n"
        f"INPUT:\n{json.dumps(haiku_input, ensure_ascii=False, indent=2)}"
    )
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=400,
                system=[{
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},  # prompt caching pour ~80% économie sur le system prompt
                }],
                tools=[EMIT_TOOL],
                tool_choice={"type": "tool", "name": "emit_email_draft"},
                messages=[{"role": "user", "content": user_msg}],
            )
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use" and block.name == "emit_email_draft":
                    args = block.input
                    return args["subject"].strip(), [p.strip() for p in args["body_paragraphs"]]
            raise RuntimeError("Aucun tool_use dans la réponse Haiku")
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1 + attempt)
            else:
                raise last_err


def validate_draft(subject: str, body_paragraphs: list[str], ipt: dict) -> Optional[str]:
    """Renvoie un message d'erreur si la draft échoue à la validation, None sinon."""
    if len(body_paragraphs) != 3:
        return f"Attendu 3 paragraphes, reçu {len(body_paragraphs)}"

    full = subject + " " + " ".join(body_paragraphs)
    lower = full.lower()

    # 1. Banned phrases
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            return f"phrase bannie : '{phrase}'"

    # 2. Placeholder leaks
    if re.search(r"\{\{|\}\}|\{[a-zA-Z_]|\}[ ,.]|<[a-zA-Z_]+>", full):
        return "placeholder leak (accolades ou <var>)"
    if re.search(r"\b(null|None|undefined)\b", full):
        return "valeur 'null' / 'None' / 'undefined' dans la sortie"

    # 3. No exclamation marks
    if "!" in full:
        return "point d'exclamation détecté"

    # 4. Peer chain présent et exact
    if ipt["peer_chain_hint"] not in body_paragraphs[1]:
        return "peer_chain_hint absent ou modifié dans le paragraphe 2"

    # 5. Cross-country peer mentions
    cross_peers = {
        "US": ["David Lloyd", "Fitness First", "Anytime Fitness"],
        "GB": ["Equinox", "CorePower", "Fitness First"],
        "AU": ["David Lloyd", "Equinox", "CorePower"],
    }
    for forbidden in cross_peers.get(ipt["establishment_country"], []):
        if forbidden in body_paragraphs[1] and forbidden not in ipt["peer_chain_hint"]:
            return f"peer cross-country : {forbidden} pour {ipt['establishment_country']}"

    # 6. Greeting cohérent avec is_generic_inbox
    greet = body_paragraphs[0].lower()
    if ipt["is_generic_inbox"]:
        if not (greet.startswith("hi team at") or greet.startswith("hello team at")):
            return "boîte générique mais greeting personnel"
    else:
        fn = (ipt.get("decision_maker_first_name") or "").lower()
        if fn and fn not in greet:
            return f"nominatif mais first_name '{fn}' absent du greeting"

    # 7. City interdite si null
    if not ipt.get("establishment_city"):
        # 1ère phrase du paragraphe 1 ne doit pas contenir " in <X>"
        first_sentence = body_paragraphs[1].split(".")[0]
        if re.search(r"\bin [A-Z][a-zA-Z]+", first_sentence):
            return "city null mais une ville est mentionnée"

    # 8. Subject : casse + longueur + first_name interdit
    if len(subject) > 70:
        return f"sujet trop long : {len(subject)} chars"
    if subject.upper() == subject and any(c.isalpha() for c in subject):
        return "sujet en ALL CAPS"
    fn = (ipt.get("decision_maker_first_name") or "").strip()
    if fn and fn in subject:
        return "first_name présent dans le sujet (interdit)"

    return None


# --------------------------------------------------------------------------- #
# Rendu HTML
# --------------------------------------------------------------------------- #


def render_html(template: str, body_paragraphs: list[str], establishment_name: str,
                city: Optional[str], unsub_token: str, cta_url: str) -> str:
    body_html = "\n              ".join(
        f'<p style="margin:0 0 14px 0;">{escape(p)}</p>' for p in body_paragraphs
    )
    city_suffix = f" ({escape(city)})" if city else ""
    return (template
            .replace("{{BODY_HTML}}", body_html)
            .replace("{{ESTAB_NAME}}", escape(establishment_name))
            .replace("{{CITY_SUFFIX}}", city_suffix)
            .replace("{{UNSUB_TOKEN}}", unsub_token)
            .replace("{{CTA_URL}}", escape(cta_url, quote=True))
            .replace("{{PRIVACY_URL}}", escape(PRIVACY_URL, quote=True)))


def render_plain(body_paragraphs: list[str], establishment_name: str,
                 city: Optional[str], cta_url: str) -> str:
    """Version plain text pour archivage + fallback éventuel."""
    parts = list(body_paragraphs)
    parts.append("")
    parts.append(f"Claim your spot on the map: {cta_url}")
    parts.append("Two minutes — free registration.")
    parts.append("")
    parts.append("More than ever, the world needs physical and mental wellness — be part of the solution.")
    parts.append("")
    parts.append("Warm regards,")
    parts.append("Jean-Guy de Gabriac")
    parts.append("Founder — World Wellness Weekend")
    parts.append("International non-profit association")
    parts.append("")
    parts.append("---")
    loc = f" ({city})" if city else ""
    parts.append(f"Tip Touch International SRL · Rue de la Loi 26, 1040 Brussels, Belgium · BE 0845.876.424")
    parts.append(f"You received this because your role at {establishment_name}{loc} is publicly listed for a global wellness initiative.")
    parts.append(f"Unsubscribe: https://unsubscribe.wellmap.org/u?t=TOKEN · Privacy: {PRIVACY_URL} · Reply STOP to opt out.")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Sélection des destinataires (stratification)
# --------------------------------------------------------------------------- #


def fetch_candidates(sb, campaign: str, country: Optional[str] = None) -> list[dict]:
    """Récupère tous les destinataires éligibles du batch :
       - Segment A : contacts valides nominatifs liés à un établissement du batch
       - Segment B : établissements no_email + generic_email_status=valid du batch
       Retourne une liste de dicts {segment, contact (ou None), establishment, recipient_email}."""
    # Pagination Supabase
    PAGE = 1000

    # Segment A — contacts valid liés au batch
    seg_a = []
    offset = 0
    while True:
        q = (sb.table("contacts")
             .select("id,nominative_email,first_name,role,full_name,establishments!inner(id,name,city,country,category,batch)")
             .eq("email_status", "valid")
             .eq("establishments.batch", campaign)
             .range(offset, offset + PAGE - 1))
        if country:
            q = q.eq("establishments.country", country)
        rows = q.execute().data
        seg_a.extend(rows)
        if len(rows) < PAGE:
            break
        offset += PAGE

    seg_a_out = []
    for r in seg_a:
        e = r["establishments"]
        seg_a_out.append({
            "segment": "A_decision_maker",
            "contact": {
                "id": r["id"],
                "first_name": r["first_name"],
                "role": r["role"],
                "full_name": r["full_name"],
            },
            "establishment": {
                "id": e["id"],
                "name": e["name"],
                "city": e.get("city"),
                "country": e["country"],
                "category": e.get("category"),
            },
            "recipient_email": r["nominative_email"],
        })

    # Segment B — establishments génériques valid
    seg_b = []
    offset = 0
    while True:
        q = (sb.table("establishments")
             .select("id,name,city,country,category,generic_email")
             .eq("batch", campaign)
             .eq("enrichment_status", "no_email")
             .not_.is_("generic_email", "null")
             .eq("generic_email_status", "valid")
             .range(offset, offset + PAGE - 1))
        if country:
            q = q.eq("country", country)
        rows = q.execute().data
        seg_b.extend(rows)
        if len(rows) < PAGE:
            break
        offset += PAGE

    seg_b_out = []
    for e in seg_b:
        seg_b_out.append({
            "segment": "B_generic_inbox",
            "contact": None,
            "establishment": {
                "id": e["id"],
                "name": e["name"],
                "city": e.get("city"),
                "country": e["country"],
                "category": e.get("category"),
            },
            "recipient_email": e["generic_email"],
        })

    return seg_a_out + seg_b_out


def stratified_sample(candidates: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Échantillon stratifié par pays × segment."""
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[dict]] = {}
    for c in candidates:
        key = (c["establishment"]["country"], c["segment"])
        buckets.setdefault(key, []).append(c)
    # Allocation proportionnelle
    total = sum(len(v) for v in buckets.values())
    out = []
    for key, items in buckets.items():
        share = round(n * len(items) / total)
        share = max(1, min(share, len(items)))
        out.extend(rng.sample(items, share))
    rng.shuffle(out)
    return out[:n]


# --------------------------------------------------------------------------- #
# Insertion en base
# --------------------------------------------------------------------------- #


def upsert_draft(sb, row: dict, ipt: dict, subject: str, body_paragraphs: list[str],
                 body_html: str, body_plain: str, campaign: str, model: str,
                 draft_id: str) -> dict:
    contact_id = (row.get("contact") or {}).get("id")
    payload = {
        "id": draft_id,
        "contact_id": contact_id,
        "establishment_id": row["establishment"]["id"],
        "campaign": campaign,
        "segment": row["segment"],
        "recipient_email": row["recipient_email"],
        "subject": subject,
        "body_html": body_html,
        "body_plain": body_plain,
        "haiku_model": model,
        "haiku_input": ipt,
        "haiku_subject_variant": ipt.get("target_subject_pattern"),
        "status": "draft",
    }
    # Upsert sur (contact_id, campaign) ou (establishment_id, campaign) si segment B.
    # Ne supprime QUE les rows status=draft (un draft déjà envoyé doit rester
    # pour préserver le lien email_sends.draft_id → email_drafts.id).
    if contact_id:
        q = sb.table("email_drafts").delete().eq("contact_id", contact_id).eq("campaign", campaign).eq("status", "draft")
    else:
        q = sb.table("email_drafts").delete().is_("contact_id", "null").eq("establishment_id", row["establishment"]["id"]).eq("campaign", campaign).eq("status", "draft")
    q.execute()
    # Si un draft 'sent' existe déjà pour cette cible, on skip la regénération (idempotent)
    existing_sent = (sb.table("email_drafts")
                     .select("id")
                     .eq("campaign", campaign)
                     .eq("status", "sent")
                     .eq("recipient_email", row["recipient_email"])
                     .limit(1)
                     .execute().data)
    if existing_sent:
        return existing_sent[0]
    res = sb.table("email_drafts").insert(payload).execute()
    return res.data[0] if res.data else payload


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", type=int, help="N destinataires stratifiés (par pays × segment)")
    g.add_argument("--all", action="store_true", help="Tous les éligibles (~1448)")
    ap.add_argument("--country", choices=["US", "GB", "AU"], help="Restreindre à un pays")
    ap.add_argument("--campaign", default=CAMPAIGN)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    client = Anthropic(api_key=CLAUDE_KEY)
    template = RENDER_TEMPLATE_PATH.read_text()

    print(f"📥 Chargement des candidats (campaign={args.campaign}"
          + (f", country={args.country}" if args.country else "") + ")…")
    candidates = fetch_candidates(sb, args.campaign, args.country)
    print(f"   {len(candidates)} candidats éligibles")

    if args.sample:
        recipients = stratified_sample(candidates, args.sample, seed=args.seed)
    else:
        recipients = candidates

    print(f"🎯 {len(recipients)} drafts à générer\n")

    stats = {"ok": 0, "validation_fail": 0, "api_error": 0}
    for i, row in enumerate(recipients, 1):
        e = row["establishment"]
        rec = row["recipient_email"]
        print(f"[{i}/{len(recipients)}] {e['country']} | {row['segment'][0]} | {e['name'][:35]:35} → {rec}", flush=True)

        try:
            ipt = build_haiku_input(row)
        except Exception as ex:
            print(f"   ⚠️  build_input : {ex}", file=sys.stderr)
            stats["api_error"] += 1
            continue

        # 1 retry sur échec de validation
        for attempt in range(2):
            try:
                subject, paragraphs = call_haiku(client, ipt)
            except Exception as ex:
                print(f"   ❌ API Haiku : {str(ex)[:80]}", file=sys.stderr)
                stats["api_error"] += 1
                break
            err = validate_draft(subject, paragraphs, ipt)
            if err is None:
                # OK — rendu HTML + plain + insertion
                draft_id = str(uuid.uuid4())  # pré-génère l'UUID → sert d'ID en base ET de utm_content
                cta_url = build_cta_url(draft_id, args.campaign, ipt.get("target_subject_pattern"))
                unsub_token = row["establishment"]["id"]  # simple token = establishment_id (à remplacer par HMAC en prod)
                body_html = render_html(template, paragraphs, e["name"], e.get("city"), unsub_token, cta_url)
                body_plain = render_plain(paragraphs, e["name"], e.get("city"), cta_url)
                upsert_draft(sb, row, ipt, subject, paragraphs, body_html, body_plain, args.campaign, HAIKU_MODEL, draft_id)
                print(f"   ✅ {subject}")
                stats["ok"] += 1
                break
            else:
                if attempt == 0:
                    print(f"   ⚠️  validation échouée ({err}) — retry")
                else:
                    print(f"   ❌ validation échouée 2× ({err}) — skip", file=sys.stderr)
                    stats["validation_fail"] += 1

    print("\n===== RÉCAP =====")
    for k, v in stats.items():
        print(f"  {k:>16} : {v}")


if __name__ == "__main__":
    main()
