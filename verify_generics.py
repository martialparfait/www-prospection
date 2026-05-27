"""
Vérifie les emails génériques (info@, contact@) des établissements
sans contact décideur identifié (Segment B).
MX (gratuit) + NeverBounce, puis met à jour establishments.generic_email_status.

Usage : python3 verify_generics.py [--limit N]
"""

import argparse
import os
import sys
import time

import requests
import dns.resolver
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
    except Exception:
        pass
    return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    q = (sb.table("establishments")
         .select("id,name,generic_email")
         .eq("enrichment_status", "no_email")
         .not_.is_("generic_email", "null")
         .is_("generic_email_status", "null"))
    if args.limit:
        q = q.limit(args.limit)
    rows = q.execute().data
    print(f"{len(rows)} emails génériques à vérifier\n")

    stats = {}
    for i, e in enumerate(rows, 1):
        email = e["generic_email"]
        if not verify_mx(email):
            status = "invalid"
        else:
            status = NB_MAP.get(verify_neverbounce(email), "unknown")
        verified_at = time.strftime("%Y-%m-%dT%H:%M:%S%z") if status in ("valid", "catch_all") else None
        try:
            sb.table("establishments").update({
                "generic_email_status": status,
                "generic_email_verified_at": verified_at,
            }).eq("id", e["id"]).execute()
        except Exception as ex:
            print(f"   ⚠️ {str(ex)[:60]}", file=sys.stderr)
            continue
        stats[status] = stats.get(status, 0) + 1
        print(f"[{i}/{len(rows)}] {e['name'][:35]:35} {email:35} {status}")

    print("\n===== RÉCAP génériques =====")
    for k in ("valid", "catch_all", "invalid", "unknown"):
        print(f"  {k}: {stats.get(k, 0)}")


if __name__ == "__main__":
    main()
