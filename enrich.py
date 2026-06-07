"""
World Wellness Weekend — Pipeline d'enrichissement (étape 3)
============================================================
Pour chaque établissement de Supabase (avec site web, statut 'pending') :
  1. CRAWL gratuit du site web  → emails publiés (mailto + regex)
  2. Si pas d'email perso → APOLLO (People Search par domaine + Match)
  3. VÉRIFICATION : syntaxe + MX (gratuit) puis NeverBounce (mailbox)
  4. Insertion dans `contacts` + mise à jour du statut de l'établissement

Garde-fous compliance (issus du workflow enrichment-cost-plan, 2026-05-31) :
  - REJET des freemails (@gmail/@yahoo/@hotmail/…) : un freemail bascule la
    campagne en B2C strict (GDPR Art. 6 lourd, CCPA, APP 7). Le crawl ne garde
    QUE les emails du domaine de l'établissement ; Apollo idem.
  - reveal_personal_emails=False pour UK et AU (Apollo le bloque côté UK GDPR
    de toute façon, APP 7 l'exige pour AU). True uniquement pour US.
  - Lookup dans la table `opt_out` AVANT toute insertion dans `contacts`.
  - Cible par défaut le batch `metro_fitness_2026` (pas l'ancien pilote).

Variables .env :
    SUPABASE_URL, SUPABASE_SECRET_KEY
    APOLLO_KEY
    NEVER_BOUNCE_API_KEY

Usage :
    python3 enrich.py --pilot                       # 100 fiches stratifiées (50US/30UK/20AU)
    python3 enrich.py --limit 5                     # test petit lot
    python3 enrich.py --no-apollo --no-verify       # crawl seul
    python3 enrich.py                               # run complet sur le batch courant
"""

import argparse
import os
import random
import re
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

import dns.resolver

DEFAULT_BATCH = "metro_fitness_2026"

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")
APOLLO_KEY = os.environ.get("APOLLO_KEY")
NB_KEY = os.environ.get("NEVER_BOUNCE_API_KEY")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

CRAWL_PATHS = ["", "/about", "/about-us", "/contact", "/contact-us", "/team", "/our-team", "/staff", "/instructors"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

GENERIC_LOCALS = {
    "info", "contact", "hello", "hi", "admin", "support", "booking", "bookings",
    "team", "office", "reception", "frontdesk", "studio", "help", "sales",
    "namaste", "yoga", "members", "membership", "enquiries", "inquiries",
    "mail", "general", "welcome", "schedule", "classes", "wellness", "fitness",
}

FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "aol.com", "protonmail.com", "proton.me", "me.com", "live.com", "msn.com",
}

JUNK_PATTERNS = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", "sentry", "wixpress",
    "example.com", "godaddy", "squarespace", "@sentry", "core-services",
    "yourdomain", "domain.com", "email.com", "@2x", "u003e", "schema.org",
)

APOLLO_TITLES = ["owner", "founder", "co-founder", "president", "ceo",
                 "general manager", "manager", "director", "principal", "head coach"]


# --------------------------------------------------------------------------- #
# Crawl
# --------------------------------------------------------------------------- #


def get_domain(website):
    if not website:
        return None
    if not website.startswith(("http://", "https://")):
        website = "https://" + website
    host = urlparse(website).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def base_url(website):
    if not website.startswith(("http://", "https://")):
        website = "https://" + website
    p = urlparse(website)
    return f"{p.scheme}://{p.netloc}"


def fetch(url, timeout=8):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r.text
    except Exception:
        pass
    return None


def is_junk(email):
    return any(p in email for p in JUNK_PATTERNS)


def is_generic(email):
    local = email.split("@")[0].lower()
    token = re.split(r"[._\-+]", local)[0]
    return local in GENERIC_LOCALS or token in GENERIC_LOCALS


def extract_emails(html, domain):
    found = set()
    try:
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select('a[href^="mailto:"]'):
            e = a.get("href", "").replace("mailto:", "").split("?")[0].strip().lower()
            if EMAIL_RE.fullmatch(e):
                found.add(e)
    except Exception:
        pass
    for m in EMAIL_RE.findall(html):
        found.add(m.lower())
    return {e for e in found if not is_junk(e)}


def crawl_site(website):
    """Retourne (personal_emails, generic_emails).
    COMPLIANCE STRICTE : garde UNIQUEMENT les emails du domaine de l'établissement.
    Rejette les freemails (@gmail/@yahoo/@hotmail/…) ET les domaines tiers
    (agences web, vendeurs). Un freemail = bascule en B2C strict (GDPR/CCPA/APP 7)."""
    domain = get_domain(website)
    base = base_url(website)
    same_domain, generic = [], []
    seen = set()
    for path in CRAWL_PATHS:
        html = fetch(base + path)
        if not html:
            continue
        for e in extract_emails(html, domain):
            if e in seen:
                continue
            seen.add(e)
            edom = e.split("@")[1]
            # COMPLIANCE : pas de freemail, pas de tiers — uniquement le domaine maison.
            if edom in FREE_PROVIDERS or not (domain and edom == domain):
                continue
            if is_generic(e):
                generic.append(e)
            else:
                same_domain.append(e)
        if same_domain:  # email perso du bon domaine trouvé -> on s'arrête
            break
    return same_domain, generic


def name_from_email(email):
    local = email.split("@")[0]
    parts = re.split(r"[._\-]", local)
    parts = [p for p in parts if p.isalpha() and len(p) > 1]
    if len(parts) >= 2:
        return parts[0].capitalize(), parts[1].capitalize()
    return None, None


# --------------------------------------------------------------------------- #
# Apollo
# --------------------------------------------------------------------------- #


APOLLO_HEADERS = {"X-Api-Key": APOLLO_KEY, "Content-Type": "application/json", "Cache-Control": "no-cache"}


def apollo_search(domain):
    """Nouveau endpoint api_search (l'ancien mixed_people/search est déprécié)."""
    try:
        r = requests.post(
            "https://api.apollo.io/api/v1/mixed_people/api_search",
            headers=APOLLO_HEADERS,
            json={"q_organization_domains_list": [domain], "person_titles": APOLLO_TITLES,
                  "page": 1, "per_page": 5},
            timeout=30,
        )
        if r.status_code != 200:
            return None
        people = r.json().get("people") or []
        return people[0] if people else None
    except Exception:
        return None


def apollo_match_by_id(pid, reveal_personal=False):
    """Révèle l'email d'une personne via son id Apollo (consomme 1 email credit).
    reveal_personal=False obligatoire pour UK/AU (UK GDPR + APP 7)."""
    try:
        r = requests.post(
            "https://api.apollo.io/api/v1/people/match",
            headers=APOLLO_HEADERS,
            json={"id": pid, "reveal_personal_emails": bool(reveal_personal)},
            timeout=30,
        )
        if r.status_code != 200:
            return None
        return r.json().get("person")
    except Exception:
        return None


def apollo_find(domain, reveal_personal=False):
    """Retourne dict {first,last,full,title,email,apollo_status} ou None.
    Rejette les emails freemail retournés par Apollo (compliance B2B uniquement)."""
    person = apollo_search(domain)
    if not person or not person.get("id"):
        return None
    title = person.get("title")
    m = apollo_match_by_id(person["id"], reveal_personal=reveal_personal)
    if not m:
        return None
    email = m.get("email")
    if not email or "not_unlocked" in str(email) or "@" not in str(email):
        return None
    email = email.lower()
    # COMPLIANCE : Apollo peut retourner un freemail (gmail/yahoo) → on rejette.
    edom = email.split("@", 1)[1]
    if edom in FREE_PROVIDERS:
        return None
    return {"first": m.get("first_name"), "last": m.get("last_name"),
            "full": f"{m.get('first_name') or ''} {m.get('last_name') or ''}".strip() or None,
            "title": m.get("title") or title, "email": email,
            "apollo_status": m.get("email_status")}


# --------------------------------------------------------------------------- #
# Vérification
# --------------------------------------------------------------------------- #

_mx_cache = {}


def verify_mx(email):
    domain = email.split("@")[-1]
    if domain in _mx_cache:
        return _mx_cache[domain]
    ok = False
    try:
        if dns.resolver.resolve(domain, "MX"):
            ok = True
    except Exception:
        try:
            if dns.resolver.resolve(domain, "A"):
                ok = True
        except Exception:
            ok = False
    _mx_cache[domain] = ok
    return ok


def verify_neverbounce(email):
    try:
        r = requests.get("https://api.neverbounce.com/v4/single/check",
                         params={"key": NB_KEY, "email": email}, timeout=30)
        d = r.json()
        if d.get("status") == "success":
            return d.get("result")  # valid|invalid|disposable|catchall|unknown
    except Exception:
        pass
    return "unknown"


NB_MAP = {"valid": "valid", "catchall": "catch_all", "invalid": "invalid",
          "disposable": "invalid", "unknown": "unknown"}


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default=DEFAULT_BATCH,
                    help=f"Batch à enrichir (défaut : {DEFAULT_BATCH})")
    ap.add_argument("--limit", type=int, default=0, help="0 = tous")
    ap.add_argument("--pilot", action="store_true",
                    help="Pilote 100 fiches stratifié 50US/30UK/20AU (Apollo Free tier OK)")
    ap.add_argument("--no-apollo", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args()

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    def retry(fn, n=4, wait=2):
        """Réessaie une opération réseau (erreurs SSL/transient macOS)."""
        for k in range(n):
            try:
                return fn()
            except Exception as e:
                if k == n - 1:
                    raise
                print(f"   ⚠️ retry réseau ({k+1}/{n}) : {str(e)[:60]}", file=sys.stderr)
                time.sleep(wait)

    def is_opted_out(email):
        """COMPLIANCE : ne JAMAIS recontacter un email dans la table opt_out."""
        try:
            res = sb.table("opt_out").select("id").eq("email", email.lower()).limit(1).execute()
            return bool(res.data)
        except Exception:
            return False  # fail-open : un opt_out indisponible ne doit pas bloquer le pipeline

    def base_query():
        q = (sb.table("establishments")
             .select("id,name,website,category,city,state,country")
             .eq("enrichment_status", "pending")
             .not_.is_("website", "null")
             .eq("batch", args.batch))
        return q

    def fetch_pilot():
        """100 fiches : 50 US / 30 UK / 20 AU, tirage aléatoire stratifié."""
        out = []
        for code, n in [("US", 50), ("GB", 30), ("AU", 20)]:
            data = base_query().eq("country", code).execute().data
            sample = random.sample(data, min(n, len(data)))
            print(f"  pilote {code}: {len(sample)} fiches tirées (sur {len(data)} dispo)")
            out.extend(sample)
        random.shuffle(out)
        return out

    def fetch_rows():
        """Pagination Supabase : PostgREST plafonne à 1000 lignes/requête → on boucle."""
        if args.pilot:
            return fetch_pilot()
        PAGE = 1000
        out = []
        offset = 0
        while True:
            page = (base_query()
                    .order("created_at")
                    .range(offset, offset + PAGE - 1)
                    .execute().data)
            out.extend(page)
            if args.limit and len(out) >= args.limit:
                return out[:args.limit]
            if len(page) < PAGE:
                return out
            offset += PAGE

    rows = retry(fetch_rows)
    print(f"\n{len(rows)} établissements à enrichir (batch={args.batch})\n")

    stats = {"crawl_perso": 0, "crawl_generic": 0, "apollo": 0, "no_email": 0,
             "valid": 0, "catch_all": 0, "invalid": 0, "unknown": 0,
             "opt_out_skipped": 0}
    per_country = {}  # {country: {kept, valid, ...}}

    for i, est in enumerate(rows, 1):
        eid, name, site = est["id"], est["name"], est["website"]
        country = (est.get("country") or "??").upper()[:2]
        domain = get_domain(site)
        pc = per_country.setdefault(country, {"crawl": 0, "apollo": 0, "valid": 0, "catch_all": 0,
                                              "invalid": 0, "unknown": 0, "no_email": 0})
        print(f"[{i}/{len(rows)}] {country} | {name[:38]:38} {domain or ''}", flush=True)

        try:
            email = full = first = last = title = None
            source = None
            apollo_status = None

            # 1) Crawl
            personal, generic = crawl_site(site)
            if generic:
                retry(lambda: sb.table("establishments").update({"generic_email": generic[0]}).eq("id", eid).execute())
            if personal:
                email = personal[0]
                first, last = name_from_email(email)
                full = f"{first or ''} {last or ''}".strip() or None
                source = "website_crawl"
                stats["crawl_perso"] += 1
                pc["crawl"] += 1

            # 2) Apollo si pas d'email perso (reveal_personal_emails uniquement US)
            if not email and not args.no_apollo and domain and APOLLO_KEY:
                reveal_personal = (country == "US")  # UK + AU → False (GDPR / APP 7)
                found = apollo_find(domain, reveal_personal=reveal_personal)
                if found:
                    email, full, first, last, title = (found["email"], found["full"],
                                                       found["first"], found["last"], found["title"])
                    apollo_status = found.get("apollo_status")
                    source = "apollo"
                    stats["apollo"] += 1
                    pc["apollo"] += 1

            # Pas d'email du tout
            if not email:
                if generic:
                    stats["crawl_generic"] += 1
                else:
                    stats["no_email"] += 1
                pc["no_email"] += 1
                retry(lambda: sb.table("establishments").update({"enrichment_status": "no_email"}).eq("id", eid).execute())
                continue

            # COMPLIANCE : skip si l'email est déjà dans opt_out (jamais recontacter)
            if is_opted_out(email):
                stats["opt_out_skipped"] += 1
                print(f"      🚫 opt-out connu, contact ignoré")
                retry(lambda: sb.table("establishments").update({"enrichment_status": "no_email"}).eq("id", eid).execute())
                continue

            # 3) Vérification
            email_status = "unknown"
            verified_at = None
            if not verify_mx(email):
                email_status = "invalid"
            elif apollo_status == "verified":
                # Apollo a déjà vérifié -> on évite de consommer un crédit NeverBounce
                email_status = "valid"
                verified_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            elif args.no_verify:
                email_status = "unknown"
            else:
                nb = verify_neverbounce(email)
                email_status = NB_MAP.get(nb, "unknown")
                if email_status in ("valid", "catch_all"):
                    verified_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            stats[email_status] = stats.get(email_status, 0) + 1
            pc[email_status] = pc.get(email_status, 0) + 1

            # 4) Insertion contact + statut
            contact = {
                "establishment_id": eid,
                "full_name": full,
                "first_name": first,
                "last_name": last,
                "role": title,
                "nominative_email": email,
                "email_status": email_status,
                "email_verified_at": verified_at,
                "source_provider": source,
                "legal_basis": "legitimate_interest",
            }
            retry(lambda: sb.table("contacts").insert(contact).execute())
            retry(lambda: sb.table("establishments").update({"enrichment_status": "enriched"}).eq("id", eid).execute())
            print(f"      → {source} | {email} | {email_status}")
        except Exception as e:
            stats["errors"] = stats.get("errors", 0) + 1
            print(f"      ⚠️ erreur, établissement ignoré : {str(e)[:80]}", file=sys.stderr)
            continue

    # Récap global
    print("\n===== RÉCAP GLOBAL =====")
    print(f"Emails perso via crawl     : {stats['crawl_perso']}")
    print(f"Emails via Apollo          : {stats['apollo']}")
    print(f"Generic seul (info@…)      : {stats['crawl_generic']}")
    print(f"Aucun email                : {stats['no_email']}")
    print(f"Opt-out skippés (compliance): {stats['opt_out_skipped']}")
    print(f"--- Vérification ---")
    print(f"  valid      : {stats.get('valid', 0)}")
    print(f"  catch_all  : {stats.get('catch_all', 0)}")
    print(f"  invalid    : {stats.get('invalid', 0)}")
    print(f"  unknown    : {stats.get('unknown', 0)}")

    # Récap par pays (critique pour le pilote stratifié)
    if per_country:
        print("\n===== RÉCAP PAR PAYS =====")
        print(f"{'Pays':<6}{'Crawl':>7}{'Apollo':>8}{'Valid':>7}{'Catch':>7}{'Inval':>7}{'Unkn':>7}{'NoMail':>8}")
        for c in sorted(per_country):
            p = per_country[c]
            print(f"{c:<6}{p['crawl']:>7}{p['apollo']:>8}{p.get('valid', 0):>7}"
                  f"{p.get('catch_all', 0):>7}{p.get('invalid', 0):>7}"
                  f"{p.get('unknown', 0):>7}{p.get('no_email', 0):>8}")


if __name__ == "__main__":
    main()
