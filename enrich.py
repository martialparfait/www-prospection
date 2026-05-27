"""
World Wellness Weekend — Pipeline d'enrichissement (étape 3)
============================================================
Pour chaque établissement de Supabase (avec site web, statut 'pending') :
  1. CRAWL gratuit du site web  → emails publiés (mailto + regex)
  2. Si pas d'email perso → APOLLO (People Search par domaine + Match)
  3. VÉRIFICATION : syntaxe + MX (gratuit) puis NeverBounce (mailbox)
  4. Insertion dans `contacts` + mise à jour du statut de l'établissement

Variables .env :
    SUPABASE_URL, SUPABASE_SECRET_KEY
    APOLLO_KEY
    NEVER_BOUNCE_API_KEY

Usage :
    python3 enrich.py --limit 15 --no-apollo --no-verify   # test crawl seul
    python3 enrich.py --limit 5                             # test complet petit lot
    python3 enrich.py                                       # run complet
"""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

import dns.resolver

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
    Garde uniquement les emails du même domaine OU d'un fournisseur gratuit
    (gmail, yahoo…). Rejette les domaines tiers (agences web, vendeurs)."""
    domain = get_domain(website)
    base = base_url(website)
    same_domain, free_prov, generic = [], [], []
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
            keep = (domain and edom == domain) or edom in FREE_PROVIDERS
            if not keep:
                continue  # domaine tiers (vendeur) -> ignoré
            if is_generic(e):
                generic.append(e)
            elif domain and edom == domain:
                same_domain.append(e)
            else:
                free_prov.append(e)
        if same_domain:  # email perso du bon domaine trouvé -> on s'arrête
            break
    return same_domain + free_prov, generic


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


def apollo_match_by_id(pid):
    """Révèle l'email d'une personne via son id Apollo (consomme 1 crédit)."""
    try:
        r = requests.post(
            "https://api.apollo.io/api/v1/people/match",
            headers=APOLLO_HEADERS,
            json={"id": pid, "reveal_personal_emails": True},
            timeout=30,
        )
        if r.status_code != 200:
            return None
        return r.json().get("person")
    except Exception:
        return None


def apollo_find(domain):
    """Retourne dict {first,last,full,title,email,apollo_status} ou None."""
    person = apollo_search(domain)
    if not person or not person.get("id"):
        return None
    title = person.get("title")
    m = apollo_match_by_id(person["id"])
    if not m:
        return None
    email = m.get("email")
    if not email or "not_unlocked" in str(email) or "@" not in str(email):
        return None
    return {"first": m.get("first_name"), "last": m.get("last_name"),
            "full": f"{m.get('first_name') or ''} {m.get('last_name') or ''}".strip() or None,
            "title": m.get("title") or title, "email": email.lower(),
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
    ap.add_argument("--limit", type=int, default=0, help="0 = tous")
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

    def fetch_rows():
        q = (sb.table("establishments")
             .select("id,name,website,category,city,state")
             .eq("enrichment_status", "pending")
             .not_.is_("website", "null")
             .order("created_at"))
        if args.limit:
            q = q.limit(args.limit)
        return q.execute().data

    rows = retry(fetch_rows)
    print(f"{len(rows)} établissements à enrichir\n")

    stats = {"crawl_perso": 0, "crawl_generic": 0, "apollo": 0, "no_email": 0,
             "valid": 0, "catch_all": 0, "invalid": 0, "unknown": 0}

    for i, est in enumerate(rows, 1):
        eid, name, site = est["id"], est["name"], est["website"]
        domain = get_domain(site)
        print(f"[{i}/{len(rows)}] {name[:40]:40} {domain or ''}", flush=True)

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

            # 2) Apollo si pas d'email perso
            if not email and not args.no_apollo and domain and APOLLO_KEY:
                found = apollo_find(domain)
                if found:
                    email, full, first, last, title = (found["email"], found["full"],
                                                       found["first"], found["last"], found["title"])
                    apollo_status = found.get("apollo_status")
                    source = "apollo"
                    stats["apollo"] += 1

            # Pas d'email du tout
            if not email:
                if generic:
                    stats["crawl_generic"] += 1
                else:
                    stats["no_email"] += 1
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

    # Récap
    print("\n===== RÉCAP =====")
    print(f"Emails perso via crawl : {stats['crawl_perso']}")
    print(f"Emails via Apollo      : {stats['apollo']}")
    print(f"Generic seul (info@…)  : {stats['crawl_generic']}")
    print(f"Aucun email            : {stats['no_email']}")
    print(f"--- Vérification ---")
    print(f"  valid      : {stats.get('valid',0)}")
    print(f"  catch_all  : {stats.get('catch_all',0)}")
    print(f"  invalid    : {stats.get('invalid',0)}")
    print(f"  unknown    : {stats.get('unknown',0)}")


if __name__ == "__main__":
    main()
