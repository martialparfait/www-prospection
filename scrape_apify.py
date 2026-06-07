"""
World Wellness Weekend — Pipeline de scraping (étape 2)
=======================================================
Collecte des établissements via Apify Google Maps Scraper
(compass/crawler-google-places), normalisation, déduplication,
filtrage qualité, puis insertion dans la table `establishments` de Supabase.

Campagne « metro_fitness_2026 » : clubs de fitness PREMIUM et MID-RANGE
dans les grandes métropoles, USA (50%) / UK (30%) / Australie (20%).
Canada EXCLU (CASL — opt-in obligatoire).

Deux familles de recherches par ville :
  - termes génériques premium/mid-range (filtre ≥50 avis)
  - requêtes par enseigne (Equinox, David Lloyd, Saint Haven…) — seuil
    d'avis abaissé car pré-qualifiées premium (capte les boutiques récentes)

Garde-fous (issus de la recherche web vérifiée) :
  - le filtre ≥50 avis n'élimine PAS le budget (Planet Fitness, PureGym,
    Jetts ont énormément d'avis) → filtre d'EXCLUSION PAR NOM par pays
  - dédup intra-run (placeId + nom/ville) ET contre la base existante
  - tag `batch` pour séparer ce jeu de l'ancien pilote

Prérequis :
    pip install -r requirements.txt

Variables d'environnement (.env à la racine) :
    APIFY_KEY, SUPABASE_URL, SUPABASE_SECRET_KEY

Usage :
    python3 scrape_apify.py --dry-run            # scrape mais n'insère rien
    python3 scrape_apify.py --test               # 1 ville + 2 termes/pays (test payant minimal)
    python3 scrape_apify.py --country US          # un seul pays
    python3 scrape_apify.py                       # run complet (~5000 cible)
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
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

APIFY_ACTOR = "compass~crawler-google-places"
APIFY_ENDPOINT = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"

SOURCE = "apify_google_maps"

# Filtres qualité (s'appliquent à tous les profils).
MIN_REVIEWS = 50           # termes génériques
PREMIUM_MIN_REVIEWS = 15   # requêtes par enseigne (capte les boutiques récentes)

# Plafonds Apify par recherche (les requêtes enseigne renvoient peu → cap bas = économie).
GENERIC_MAX_PER_SEARCH = 60
CHAIN_MAX_PER_SEARCH = 30

# Filtres catégorie / nom — un set par profil (cf. PROFILES plus bas).
FITNESS_CAT_HINTS = (
    "gym", "fitness", "health club", "physical fitness", "personal train",
    "pilates", "yoga", "crossfit", "boxing", "martial art", "cycling studio",
    "spin", "athletic club", "bootcamp", "strength", "reformer", "barre",
)
FITNESS_NAME_HINTS = (
    "gym", "fitness", "pilates", "crossfit", "health club", "yoga",
    "barre", "cycle", "athletic club", "bootcamp",
)

# Profil yoga/pilates — focus sur les studios spécialisés.
YOGA_CAT_HINTS = (
    "yoga", "pilates", "reformer", "barre", "vinyasa", "ashtanga",
    "hot yoga", "bikram", "iyengar", "kundalini", "yin yoga",
    "meditation", "mindfulness studio",
)
YOGA_NAME_HINTS = (
    "yoga", "pilates", "reformer", "barre", "vinyasa", "ashtanga",
    "namaste", "lagree",
)

# Variables module-level mutables — main() les assigne selon --profile.
CAMPAIGN_BATCH = "metro_fitness_2026"
CATEGORY = "fitness"
CAT_HINTS = FITNESS_CAT_HINTS
NAME_HINTS = FITNESS_NAME_HINTS

BATCH_SIZE = 500
THROTTLE_SECONDS = 1.5  # pause entre appels Apify (évite le rate-limiting / connection reset)

# Ciblage par pays (issu de la recherche web vérifiée — workflow metro-fitness-targeting).
COUNTRIES_FITNESS = {
    "US": {
        "name": "United States",
        "target": 2500,
        "cities": [
            "New York, New York", "Los Angeles, California",
            "San Francisco, California", "Chicago, Illinois",
            "Washington, District of Columbia", "Arlington, Virginia",
            "Miami, Florida", "Philadelphia, Pennsylvania",
            "Boston, Massachusetts", "Dallas, Texas", "Fort Worth, Texas",
            "Houston, Texas", "Atlanta, Georgia", "Seattle, Washington",
            "Denver, Colorado", "San Diego, California",
            "Scottsdale, Arizona", "Minneapolis, Minnesota",
        ],
        "generic_terms": [
            "luxury health club", "premium fitness club", "boutique fitness studio",
            "reformer pilates studio", "Lagree fitness studio", "athletic club and spa",
            "private personal training studio", "racquet and fitness club",
            "high-end wellness and fitness club", "boutique cycling studio",
            "luxury boutique gym",
        ],
        "chain_queries": [
            "Equinox", "Life Time", "Bay Club", "Chelsea Piers Fitness",
            "VillaSport Athletic Club", "Colorado Athletic Club", "Barry's Bootcamp",
            "SoulCycle", "Solidcore", "CorePower Yoga", "Rumble Boxing",
            "Club Pilates", "Pure Barre", "Orangetheory Fitness", "F45 Training",
        ],
        "avoid": [
            "planet fitness", "crunch", "blink fitness", "youfit", "eos fitness",
            "puregym", "esporta", "mountainside fitness", "snap fitness",
            "anytime fitness", "workout anytime", "fitness connection", "chuze",
            "retro fitness", "ufc gym", "amped fitness", "vasa fitness",
            "city sports club", "genesis health clubs",
        ],
    },
    "GB": {
        "name": "United Kingdom",
        "target": 1500,
        "cities": [
            "London, England", "Manchester, England", "Birmingham, England",
            "Leeds, England", "Glasgow, Scotland", "Edinburgh, Scotland",
            "Bristol, England", "Liverpool, England",
            "Newcastle upon Tyne, England", "Sheffield, England",
            "Nottingham, England", "Cardiff, Wales",
        ],
        "generic_terms": [
            "luxury health club", "premium gym", "boutique fitness studio",
            "reformer pilates studio", "private members health club",
            "high end gym with pool and spa", "private personal training studio",
            "boutique cycling studio", "strength and conditioning gym",
            "tennis and fitness club", "wellness club",
        ],
        "chain_queries": [
            "Third Space", "David Lloyd Clubs", "Virgin Active",
            "Nuffield Health Fitness and Wellbeing", "Bannatyne Health Club",
            "Village Gym", "Barry's Bootcamp", "Gymbox", "1Rebel", "Psycle",
            "Total Fitness", "F45 Training",
        ],
        "avoid": [
            "puregym", "the gym group", "jd gyms", "xercise4less", "easygym",
            "snap fitness", "sports direct fitness", "everlast gym", "trugym",
            "simply gym", "gym4less", "fitspace", "bloc gym", "places gym",
            "places leisure", "energie fitness", "better gym", "better leisure",
            "everyone active", "leisure centre",
        ],
    },
    "AU": {
        "name": "Australia",
        "target": 1000,
        "cities": [
            "Sydney, New South Wales", "Melbourne, Victoria",
            "Brisbane, Queensland", "Perth, Western Australia",
            "Adelaide, South Australia", "Gold Coast, Queensland",
            "Canberra, Australian Capital Territory",
            "Newcastle, New South Wales", "Sunshine Coast, Queensland",
        ],
        "generic_terms": [
            "luxury health club", "premium health club", "private wellness club",
            "boutique fitness studio", "reformer pilates studio",
            "boutique HIIT studio", "HYROX training gym",
            "functional training studio", "private personal training studio",
            "members wellness club",
        ],
        "chain_queries": [
            "Virgin Active", "Fitness First", "Goodlife Health Clubs",
            "Saint Haven", "KX Pilates", "Barry's Bootcamp",
            "BFT Body Fit Training", "F45 Training", "One Playground",
            "Genesis Fitness",
        ],
        "avoid": [
            "crunch fitness", "club lime", "revo fitness", "jetts", "snap fitness",
            "zap fitness", "top gym", "world gym", "plus fitness", "envie fitness",
            "pure health", "leisure centre", "aquatic centre",
        ],
    },
}


# Profil yoga/pilates — mêmes métropoles (les studios yoga clusterisent dans
# les mêmes zones que les boutiques fitness premium).
COUNTRIES_YOGA = {
    "US": {
        "name": "United States",
        "target": 2000,
        "cities": COUNTRIES_FITNESS["US"]["cities"],
        "generic_terms": [
            "yoga studio", "hot yoga studio", "vinyasa yoga studio",
            "ashtanga yoga studio", "reformer pilates studio",
            "classical pilates studio", "Lagree fitness studio",
            "barre studio", "boutique pilates studio",
            "private pilates studio", "rooftop yoga studio",
        ],
        "chain_queries": [
            "CorePower Yoga", "YogaSix", "YogaWorks", "Y7 Studio",
            "Modo Yoga", "Sky Ting Yoga", "Pure Yoga",
            "Club Pilates", "Solidcore", "Lagree Fitness",
            "Pure Barre", "Barre3", "The Bar Method", "Sweat Yoga",
            "Sculpt Society",
        ],
        "avoid": [
            "planet fitness", "la fitness", "24 hour fitness", "youfit",
            "crunch", "eos fitness", "blink fitness", "snap fitness",
            "anytime fitness", "ufc gym",
        ],
    },
    "GB": {
        "name": "United Kingdom",
        "target": 1200,
        "cities": COUNTRIES_FITNESS["GB"]["cities"],
        "generic_terms": [
            "yoga studio", "hot yoga studio", "vinyasa yoga studio",
            "ashtanga yoga studio", "reformer pilates studio",
            "classical pilates studio", "Lagree pilates studio",
            "barre studio", "boutique pilates studio",
            "private pilates studio", "rooftop yoga",
        ],
        "chain_queries": [
            "triyoga", "Hot Pod Yoga", "Yogahome", "More Yoga",
            "Heartcore", "Reformer Studio", "Ten Health and Fitness",
            "Bodyism", "Frame Pilates", "Psycle Yoga", "Romemo Yoga",
            "Fly LDN", "Indaba Yoga",
        ],
        "avoid": [
            "puregym", "the gym group", "jd gyms", "anytime fitness",
            "snap fitness", "leisure centre", "places leisure",
        ],
    },
    "AU": {
        "name": "Australia",
        "target": 800,
        "cities": COUNTRIES_FITNESS["AU"]["cities"],
        "generic_terms": [
            "yoga studio", "hot yoga studio", "vinyasa yoga studio",
            "ashtanga yoga studio", "reformer pilates studio",
            "classical pilates studio", "Lagree pilates studio",
            "barre studio", "boutique pilates studio",
            "private pilates studio",
        ],
        "chain_queries": [
            "KX Pilates", "Power Living Yoga", "Body Mind Life",
            "Humming Puppy", "BeReal Yoga", "Studio Pilates",
            "Pilates Performance", "Studio 99 Pilates",
            "Hot Yoga Australia", "Reformer 8", "One Hot Yoga",
            "Inspire Pilates", "Flow Athletic",
        ],
        "avoid": [
            "crunch fitness", "club lime", "snap fitness", "jetts",
            "anytime fitness", "leisure centre", "aquatic centre",
        ],
    },
}


# Profils disponibles via --profile : chaque profil décrit sa catégorie, ses
# filtres et son ciblage géographique. Le batch en DB porte le nom du profil.
PROFILES = {
    "metro_fitness_2026": {
        "category": "fitness",
        "cat_hints": FITNESS_CAT_HINTS,
        "name_hints": FITNESS_NAME_HINTS,
        "countries": COUNTRIES_FITNESS,
    },
    "yoga_pilates_2026": {
        "category": "yoga_pilates",
        "cat_hints": YOGA_CAT_HINTS,
        "name_hints": YOGA_NAME_HINTS,
        "countries": COUNTRIES_YOGA,
    },
}


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
    """minuscule + sans accents + espaces normalisés."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().split())


class ApifyQuotaError(RuntimeError):
    """Erreur dure (crédit/quota/clé) — inutile de réessayer, on arrête."""


def run_apify_search(search_term, location_query, max_results, retries=4):
    """Lance l'actor Apify avec retry + backoff sur erreurs transitoires
    (Connection reset, timeouts, 429/5xx). Lève ApifyQuotaError sur 401/402/403."""
    payload = {
        "searchStringsArray": [search_term],
        "locationQuery": location_query,
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
        "skipClosedPlaces": True,
    }
    last = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                APIFY_ENDPOINT,
                params={"token": APIFY_KEY},
                json=payload,
                timeout=600,
            )
            if resp.status_code in (401, 402, 403):
                raise ApifyQuotaError(
                    f"Apify {resp.status_code} (crédit/quota/clé) : {resp.text[:200]}"
                )
            resp.raise_for_status()
            return resp.json()
        except ApifyQuotaError:
            raise
        except Exception as e:
            last = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
    raise last


def is_budget(name, avoid_list):
    """True si le nom matche une enseigne budget à exclure (substring, insensible casse)."""
    n = normalize_text(name)
    return any(bad in n for bad in avoid_list)


def is_fitness_place(place):
    """True si le lieu match les hints du profil actif (catégorie Google ou nom).
    Le nom de la fonction est historique — fonctionne pour fitness ET yoga/pilates
    selon les CAT_HINTS / NAME_HINTS du profil sélectionné via --profile."""
    cats = place.get("categories") or []
    cat_text = normalize_text(" | ".join(list(cats) + [place.get("categoryName") or ""]))
    if any(h in cat_text for h in CAT_HINTS):
        return True
    name = normalize_text(place.get("title") or place.get("name") or "")
    return any(h in name for h in NAME_HINTS)


def to_establishment(place, country_code, default_region, min_reviews):
    """Transforme un item Apify en ligne `establishments`. Porte un seuil d'avis."""
    name = place.get("title") or place.get("name")
    if not name:
        return None

    city = place.get("city") or ""
    country = (place.get("countryCode") or country_code).upper()[:2]
    loc = place.get("location") or {}

    emails = place.get("emails") or []
    generic_email = emails[0] if emails else None

    amenities = {}
    add_info = place.get("additionalInfo") or {}
    if isinstance(add_info, dict):
        amenities = add_info

    return {
        "source": SOURCE,
        "source_id": place.get("placeId"),
        "name": name,
        "category": CATEGORY,
        "sub_categories": place.get("categories") or None,
        "address": place.get("address") or place.get("street"),
        "city": city,
        "state": place.get("state") or default_region,
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
        "batch": CAMPAIGN_BATCH,
        "enrichment_status": "pending",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        # champs internes (retirés avant insertion)
        "_min_reviews": min_reviews,
    }


def dedup(rows):
    """Déduplication mémoire : par source_id puis par dedup_key (garde le 1er vu)."""
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
    # retire les champs internes
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    inserted = 0
    for i in range(0, len(clean), BATCH_SIZE):
        batch = clean[i:i + BATCH_SIZE]
        supabase.table("establishments").insert(batch).execute()
        inserted += len(batch)
        print(f"   → inséré {inserted}/{len(clean)}")
    return inserted


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def city_search_specs(cfg, test=False):
    """Retourne [(terme, max_results, min_reviews)] à lancer pour chaque ville."""
    generic = cfg["generic_terms"][:2] if test else cfg["generic_terms"]
    chains = cfg["chain_queries"][:2] if test else cfg["chain_queries"]
    specs = [(t, GENERIC_MAX_PER_SEARCH, MIN_REVIEWS) for t in generic]
    specs += [(q, CHAIN_MAX_PER_SEARCH, PREMIUM_MIN_REVIEWS) for q in chains]
    return specs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=list(PROFILES), default="metro_fitness_2026",
                        help="Profil de campagne : metro_fitness_2026 (défaut) ou yoga_pilates_2026")
    parser.add_argument("--country", choices=["US", "GB", "AU"], help="Limiter à un pays")
    parser.add_argument("--dry-run", action="store_true", help="Scrape mais n'insère rien")
    parser.add_argument("--test", action="store_true",
                        help="Run minimal (1 ville + 2 termes/pays, sans enseignes)")
    parser.add_argument("--max", type=int, default=None,
                        help="Override du plafond résultats/recherche générique")
    parser.add_argument("--cities-from", type=int, default=1, metavar="N",
                        help="Reprise : commencer à la N-ième ville (1-indexed) du pays.")
    args = parser.parse_args()

    # Applique le profil aux variables module-level utilisées par les helpers
    # (to_establishment, is_fitness_place, etc.).
    global CAMPAIGN_BATCH, CATEGORY, CAT_HINTS, NAME_HINTS
    profile = PROFILES[args.profile]
    CAMPAIGN_BATCH = args.profile
    CATEGORY = profile["category"]
    CAT_HINTS = profile["cat_hints"]
    NAME_HINTS = profile["name_hints"]
    COUNTRIES = profile["countries"]

    print(f"🎯 Profil actif : {args.profile} (category={CATEGORY})")

    check_config()
    supabase = None if args.dry_run else create_client(SUPABASE_URL, SUPABASE_KEY)

    codes = [args.country] if args.country else list(COUNTRIES)
    totals = {}

    for code in codes:
        cfg = COUNTRIES[code]
        cities = cfg["cities"][:1] if args.test else cfg["cities"]
        if args.cities_from > 1:
            cities = cfg["cities"][args.cities_from - 1:]  # override --test
        specs = city_search_specs(cfg, test=args.test)
        c_raw = c_kept = c_inserted = 0
        print(f"\n===== {cfg['name']} ({code}) — {len(cities)} villes × {len(specs)} recherches =====",
              flush=True)

        # Insertion INCRÉMENTALE par ville (anti-crash sur un run long).
        for ci, city in enumerate(cities, 1):
            location = f"{city}, {cfg['name']}"
            region = city.split(",")[-1].strip()
            rows = []
            for term, mx, mr in specs:
                time.sleep(THROTTLE_SECONDS)
                if mx == GENERIC_MAX_PER_SEARCH and args.max:
                    mx = args.max
                print(f"[{code} {ci}/{len(cities)}] {term} @ {city} (max {mx}) …", flush=True)
                try:
                    places = run_apify_search(term, location, mx)
                except ApifyQuotaError as e:
                    print(f"\n🛑 ARRÊT — crédit/quota Apify : {e}", file=sys.stderr)
                    print("   Le batch déjà inséré est conservé ; recharge Apify puis relance "
                          f"(ex. python3 scrape_apify.py --country {code}).", file=sys.stderr)
                    sys.exit(2)
                except Exception as e:
                    print(f"   ⚠️ échec (après retries) : {str(e)[:100]}", file=sys.stderr)
                    continue
                rows.extend(r for r in (to_establishment(p, code, region, mr) for p in places) if r)
            c_raw += len(rows)

            deduped = dedup(rows)
            kept, d_rev, d_bud, d_cat = [], 0, 0, 0
            for r in deduped:
                if (r.get("review_count") or 0) < r["_min_reviews"]:
                    d_rev += 1
                elif is_budget(r["name"], cfg["avoid"]):
                    d_bud += 1
                elif not is_fitness_place(r["raw_data"]):
                    d_cat += 1
                else:
                    kept.append(r)
            c_kept += len(kept)
            print(f"   {city}: {len(rows)} bruts → {len(kept)} gardés "
                  f"(écartés {d_rev}<avis / {d_bud} budget / {d_cat} cat)", flush=True)

            if args.dry_run:
                for ex in kept[:3]:
                    print(f"      • {ex['name']} | {ex['review_count']} avis | {ex.get('website')}")
                continue

            new_rows = filter_existing(supabase, kept)
            if new_rows:
                inserted = insert_rows(supabase, new_rows)
                c_inserted += inserted
                print(f"   → +{inserted} insérés (cumul {code}: {c_inserted})", flush=True)

        totals[code] = {"raw": c_raw, "kept": c_kept, "inserted": c_inserted}

    print("\n===== RÉCAP GLOBAL =====")
    for code, s in totals.items():
        print(f"  {code}: brut {s['raw']} | gardés {s['kept']} | insérés {s['inserted']} "
              f"(cible {COUNTRIES[code]['target']})")


if __name__ == "__main__":
    main()
