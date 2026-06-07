"""
Re-vérifie les contacts dont email_status='unknown' (NeverBounce a échoué
lors du run initial, typiquement crédit épuisé en cours).
MX (gratuit) + NeverBounce, puis mise à jour de contacts.email_status.

Usage : python3 reverify_unknowns.py [--batch metro_fitness_2026] [--limit N]
"""

import argparse
import os
import sys
import time

import dns.resolver
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")
NB_KEY = os.environ.get("NEVER_BOUNCE_API_KEY")

NB_MAP = {"valid": "valid", "catchall": "catch_all", "invalid": "invalid",
          "disposable": "invalid", "unknown": "unknown"}
_mx_cache = {}


def verify_mx(email):
    dom = email.split("@")[-1]
    if dom in _mx_cache:
        return _mx_cache[dom]
    ok = False
    try:
        if dns.resolver.resolve(dom, "MX"):
            ok = True
    except Exception:
        try:
            if dns.resolver.resolve(dom, "A"):
                ok = True
        except Exception:
            ok = False
    _mx_cache[dom] = ok
    return ok


def verify_neverbounce(email):
    try:
        r = requests.get("https://api.neverbounce.com/v4/single/check",
                         params={"key": NB_KEY, "email": email}, timeout=30)
        d = r.json()
        if d.get("status") == "success":
            return d.get("result")
        # Diagnostic en cas de quota
        if "credit" in (d.get("message") or "").lower():
            print(f"   🛑 NeverBounce : {d.get('message')}", file=sys.stderr)
            raise SystemExit(2)
    except SystemExit:
        raise
    except Exception:
        pass
    return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="metro_fitness_2026")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # contacts.email_status='unknown' dont l'établissement est dans le batch
    q = (sb.table("contacts")
         .select("id,nominative_email,establishment_id,establishments!inner(batch)")
         .eq("email_status", "unknown")
         .eq("establishments.batch", args.batch))
    if args.limit:
        q = q.limit(args.limit)
    rows = q.execute().data
    print(f"{len(rows)} contacts à re-vérifier (batch={args.batch})\n")

    stats = {}
    for i, c in enumerate(rows, 1):
        email = (c.get("nominative_email") or "").lower()
        if not email:
            continue
        if not verify_mx(email):
            status = "invalid"
        else:
            status = NB_MAP.get(verify_neverbounce(email), "unknown")
        verified_at = time.strftime("%Y-%m-%dT%H:%M:%S%z") if status in ("valid", "catch_all") else None
        try:
            sb.table("contacts").update({
                "email_status": status,
                "email_verified_at": verified_at,
            }).eq("id", c["id"]).execute()
        except Exception as ex:
            print(f"   ⚠️ DB update : {str(ex)[:80]}", file=sys.stderr)
            continue
        stats[status] = stats.get(status, 0) + 1
        print(f"[{i}/{len(rows)}] {email:45} → {status}")

    print("\n===== RÉCAP re-vérification contacts =====")
    for k in ("valid", "catch_all", "invalid", "unknown"):
        print(f"  {k}: {stats.get(k, 0)}")


if __name__ == "__main__":
    main()
