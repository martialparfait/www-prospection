# WWW Prospection — Contexte projet

Prospection pour **World Wellness Weekend** (client : Tip Touch International SRL, BE 0845.876.424).
Objectif : identifier les emails des responsables d'établissements bien-être (fitness, yoga, Pilates,
hôtels avec piscine+gym, dojos, running clubs) et les inviter à participer gratuitement.

## Conventions du projet

### 📋 Logs (IMPORTANT)
**Tout process长 ou script qui tourne doit écrire un fichier log dans `logs/`.**
- Format du nom : `logs/<process>_<YYYYMMDD-HHMMSS>.log`
  - ex. `logs/scrape_20260508-1432.log`, `logs/enrich_20260508-1530.log`
- Lancer les scripts longs avec redirection : `python3 script.py > "logs/<nom>_$(date +%Y%m%d-%H%M%S).log" 2>&1`
- Le dossier `logs/` est gitignoré.
- But : pouvoir suivre et auditer chaque exécution (scraping, enrichissement, envois).

### 🔐 Secrets
- Toutes les clés sont dans `.env` à la racine (gitignoré) : `SUPABASE_URL`, `SUPABASE_SECRET_KEY`,
  `SUPABASE_PASSWORD`, `APIFY_KEY`, `APOLLO_KEY`, `NEVER_BOUNCE_API_KEY`.
- Service Account Google dans `.secrets/service_account.json`.
- Ne JAMAIS afficher la valeur d'un secret en clair (logs, commits, conversation).

## Infrastructure

- **Supabase** : projet `WWW Prospection`, id `nbpvxppxflpmtifuqviz` (eu-west-1, Postgres 17).
  - Tables : `establishments`, `contacts`, `opt_out`, `campaigns`, `email_sends`. RLS activé.
  - Le pipeline backend utilise la `SUPABASE_SECRET_KEY` (bypass RLS).
- **Google Sheet** (référentiel) : `15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0`
  - Onglets : Catégories, Pays, Régions, Établissements.

## Scripts

| Fichier | Rôle |
|---|---|
| `setup_sheet.py` | (Re)construit les onglets du Google Sheet (référentiel). |
| `scrape_apify.py` | Étape 2 — scraping Apify Google Maps → `establishments`. |
| `enrich.py` | Étape 3 — crawl + Apollo + NeverBounce → `contacts`. |
| `supabase_schema.sql` | Schéma de la base (déjà appliqué). |

## Pipeline (état pilote — USA, verticaux yoga/pilates/fitness)

1. ✅ Scraping Apify → `establishments`
2. ✅ Enrichissement (crawl gratuit → Apollo → vérif NeverBounce) → `contacts`
3. ⏳ Rédaction 1er email + config SendGrid → envoi sur contacts `valid`

## Stack outils retenue

- **Apify** (Google Maps scraping) · **Apollo** (api_search → people/match par id) ·
  **NeverBounce** (vérif email) · **SendGrid** (envoi, domaine secondaire warmupé).
- Apollo : endpoint `mixed_people/api_search` (l'ancien `mixed_people/search` est déprécié).
- Conformité : crawl/Apollo uniquement (pas de scraping LinkedIn). Politique RGPD dans `privacy_policy_*.md`.
