"""
World Wellness Weekend — Pipeline de scraping (étape 2)
=======================================================
Collecte des établissements via Apify Google Maps Scraper
(compass/crawler-google-places), normalisation, déduplication,
puis insertion dans la table `establishments` de Supabase.

Pilote : USA × {yoga, pilates, fitness} × villes cibles.

Prérequis :
    pip install -r requirements.txt

Variables d'environnement (.env à la racine du projet) :
    APIFY_KEY      = token API Apify
    SUPABASE_URL   = https://xxxx.supabase.co
    SUPABASE_KEY   = service_role key (PAS la anon key)

Usage :
    python3 scrape_apify.py                 # run complet (pilote)
    python3 scrape_apify.py --max 40        # limite résultats/recherche
    python3 scrape_apify.py --dry-run       # scrape mais n'insère pas
"""

import argparse
import os
import sys
import time
import unicodedata

import requests
from dotenv import load_dotenv
from supabase import create_client


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

APIFY_KEY = os.environ.get("APIFY_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
# Clé serveur (bypass RLS) : nouveau format sb_secret_... ou legacy service_role JWT.
# On préfère SUPABASE_SECRET_KEY ; fallback sur SUPABASE_KEY pour compatibilité.
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

# Actor "Google Maps Scraper" (compass/crawler-google-places)
APIFY_ACTOR = "compass~crawler-google-places"
APIFY_ENDPOINT = (
    f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"
)

SOURCE = "apify_google_maps"

# Verticaux du pilote : clé interne -> terme de recherche Google Maps
VERTICALS = {
    "yoga": "yoga studio",
    "pilates": "pilates studio",
    "fitness": "fitness club",
}

# Villes cibles du pilote (Ville, État)
CITIES = [
    ("New York", "New York"),
    ("Los Angeles", "California"),
    ("Chicago", "Illinois"),
    ("Houston", "Texas"),
    ("Phoenix", "Arizona"),
    ("San Diego", "California"),
    ("Austin", "Texas"),
    ("Miami", "Florida"),
    ("Seattle", "Washington"),
    ("Denver", "Colorado"),
]

DEFAULT_MAX_PER_SEARCH = 80
BATCH_SIZE = 500


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def check_config():
    missing = []
    if not APIFY_KEY:
        missing.append("APIFY_KEY")
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing.append("SUPABASE_SECRET_KEY (clé serveur, bypass RLS)")
    if missing:
        print(f"❌ Variables manquantes dans .env : {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def normalize_text(s):
    """minuscule + sans accents + espaces normalisés (pour la clé de dédup)."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().split())


def run_apify_search(search_term, location_query, max_results):
    """Lance l'actor Apify et retourne la liste brute des lieux."""
    payload = {
        "searchStringsArray": [search_term],
        "locationQuery": location_query,
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
        "skipClosedPlaces": True,
    }
    resp = requests.post(
        APIFY_ENDPOINT,
        params={"token": APIFY_KEY},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()


def to_establishment(place, category):
    """Transforme un item Apify en ligne `establishments`."""
    name = place.get("title") or place.get("name")
    if not name:
        return None

    city = place.get("city") or ""
    country = (place.get("countryCode") or "US").upper()[:2]
    loc = place.get("location") or {}

    # email générique éventuel (info@, contact@) — non personnel
    emails = place.get("emails") or []
    generic_email = emails[0] if emails else None

    amenities = {}
    add_info = place.get("additionalInfo") or {}
    if isinstance(add_info, dict):
        amenities = add_info

    return {
        "source": SOURCE,
        "source_id": place.get("placeId") or place.get("placeId"),
        "name": name,
        "category": category,
        "sub_categories": place.get("categories") or None,
        "address": place.get("address") or place.get("street"),
        "city": city,
        "state": place.get("state"),
        "postal_code": place.get("postalCode"),
        "country": country,
        "latitude": loc.get("lat"),
        "longitude": loc.get("lng"),
        "phone": place.get("phone") or place.get("phoneUnformatted"),
        "website": place.get("website"),
        "generic_email": generic_email,
        "rating": place.get("totalScore"),
        "review_count": place.get("reviewsCount"),
        "amenities": amenities,
        "raw_data": place,
        "dedup_key": f"{normalize_text(name)}|{normalize_text(city)}|{country}",
        "enrichment_status": "pending",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def dedup(rows):
    """Déduplication en mémoire : par source_id puis par dedup_key."""
    seen_ids, seen_keys, out = set(), set(), []
    for r in rows:
        sid = r.get("source_id")
        key = r.get("dedup_key")
        if sid and sid in seen_ids:
            continue
        if key and key in seen_keys:
            continue
        if sid:
            seen_ids.add(sid)
        if key:
            seen_keys.add(key)
        out.append(r)
    return out


def filter_existing(supabase, rows):
    """Retire les lieux déjà présents en base (idempotence sur source_id)."""
    ids = [r["source_id"] for r in rows if r.get("source_id")]
    existing = set()
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        res = (
            supabase.table("establishments")
            .select("source_id")
            .eq("source", SOURCE)
            .in_("source_id", chunk)
            .execute()
        )
        existing.update(row["source_id"] for row in res.data)
    return [r for r in rows if r.get("source_id") not in existing]


def insert_rows(supabase, rows):
    inserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        supabase.table("establishments").insert(batch).execute()
        inserted += len(batch)
        print(f"   → inséré {inserted}/{len(rows)}")
    return inserted


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_PER_SEARCH,
                        help="Nombre max de résultats par recherche (défaut 80)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Scrape mais n'insère rien dans Supabase")
    args = parser.parse_args()

    check_config()
    supabase = None if args.dry_run else create_client(SUPABASE_URL, SUPABASE_KEY)

    all_rows = []
    total_searches = len(CITIES) * len(VERTICALS)
    n = 0

    for city, state in CITIES:
        location_query = f"{city}, {state}, United States"
        for category, term in VERTICALS.items():
            n += 1
            print(f"[{n}/{total_searches}] {term} @ {city}, {state} …", flush=True)
            try:
                places = run_apify_search(term, location_query, args.max)
            except Exception as e:
                print(f"   ⚠️ échec Apify : {e}", file=sys.stderr)
                continue
            rows = [to_establishment(p, category) for p in places]
            rows = [r for r in rows if r]
            print(f"   {len(rows)} lieux récupérés")
            all_rows.extend(rows)

    print(f"\nTotal brut : {len(all_rows)} lieux")
    deduped = dedup(all_rows)
    print(f"Après dédup mémoire : {len(deduped)} lieux")

    if args.dry_run:
        print("\n[DRY-RUN] Aucune insertion. Exemple de fiche :")
        if deduped:
            ex = deduped[0]
            for k in ("name", "category", "city", "state", "website", "phone", "rating"):
                print(f"   {k}: {ex.get(k)}")
        return

    new_rows = filter_existing(supabase, deduped)
    print(f"Après filtre doublons en base : {len(new_rows)} nouveaux lieux")

    if new_rows:
        inserted = insert_rows(supabase, new_rows)
        print(f"\n✅ {inserted} établissements insérés dans Supabase")
    else:
        print("\nRien de nouveau à insérer.")

    # Récap par catégorie
    by_cat = {}
    for r in new_rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    for c, k in by_cat.items():
        print(f"   • {c}: {k}")


if __name__ == "__main__":
    main()
