-- =============================================================================
-- World Wellness Weekend — Schéma de base de données (Supabase / PostgreSQL)
-- Pilote USA : yoga + Pilates + fitness
-- Conçu pour s'étendre ensuite à 6 verticaux × 6 pays
-- =============================================================================
-- À exécuter dans : Supabase > SQL Editor > New query
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. Extensions
-- -----------------------------------------------------------------------------
create extension if not exists "pgcrypto";      -- gen_random_uuid()
create extension if not exists "pg_trgm";        -- fuzzy matching (dédup nom/adresse)
-- create extension if not exists "postgis";     -- (optionnel) requêtes géographiques

-- -----------------------------------------------------------------------------
-- 1. Table ESTABLISHMENTS — les établissements collectés
--    (données NON personnelles : entreprise, adresse, contacts génériques)
-- -----------------------------------------------------------------------------
create table if not exists establishments (
    id               uuid primary key default gen_random_uuid(),

    -- Traçabilité de la source
    source           text not null,              -- 'apify_google_maps', 'osm', 'overture'
    source_id        text,                       -- ex. google place_id (déduplication)

    -- Identité de l'établissement
    name             text not null,
    category         text not null,              -- 'yoga' | 'pilates' | 'fitness' | 'martial_arts' | 'running' | 'hotel'
    sub_categories   text[],                     -- tags additionnels

    -- Localisation
    address          text,
    city             text,
    state            text,                       -- état US (CA, NY, TX...)
    postal_code      text,
    country          char(2) not null default 'US',  -- ISO 3166-1 alpha-2
    latitude         numeric(9,6),
    longitude        numeric(9,6),

    -- Contacts NON personnels (hors RGPD)
    phone            text,
    website          text,
    generic_email    text,                       -- info@, contact@ (pas une donnée perso)

    -- Signaux de qualité
    rating           numeric(2,1),
    review_count     integer,
    amenities        jsonb default '{}'::jsonb,  -- { "pool": true, "gym": true, ... }

    -- Données brutes et déduplication
    raw_data         jsonb,
    dedup_key        text,                       -- normalisé : lower(name)+city+country

    -- Statut pipeline
    enrichment_status text default 'pending',    -- pending | crawled | enriched | failed
    scraped_at       timestamptz,
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now()
);

-- Un même lieu ne doit pas être inséré deux fois depuis la même source
create unique index if not exists ux_estab_source
    on establishments (source, source_id)
    where source_id is not null;

create index if not exists ix_estab_dedup    on establishments using gin (dedup_key gin_trgm_ops);
create index if not exists ix_estab_name_trgm on establishments using gin (name gin_trgm_ops);
create index if not exists ix_estab_country_cat on establishments (country, category);
create index if not exists ix_estab_status   on establishments (enrichment_status);

-- -----------------------------------------------------------------------------
-- 2. Table CONTACTS — les responsables identifiés
--    (données PERSONNELLES : soumises au RGPD)
-- -----------------------------------------------------------------------------
create table if not exists contacts (
    id                  uuid primary key default gen_random_uuid(),
    establishment_id    uuid not null references establishments(id) on delete cascade,

    -- Identité du responsable
    full_name           text,
    first_name          text,
    last_name           text,
    role                text,                    -- 'owner' | 'manager' | 'general_manager'
    nominative_email    text,                    -- /!\ donnée personnelle
    linkedin_url        text,

    -- Statut de l'email
    email_status        text default 'unknown',  -- unknown | valid | risky | invalid | catch_all
    email_verified_at   timestamptz,
    source_provider     text,                    -- 'website_crawl' | 'apollo' | 'dropcontact' | 'hunter'
    confidence_score    numeric(3,2),            -- 0.00 à 1.00

    -- Conformité RGPD
    legal_basis         text default 'legitimate_interest',
    gdpr_info_sent_at   timestamptz,             -- date d'envoi du 1er email (article 14)
    opt_out_at          timestamptz,             -- désinscription

    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists ix_contact_estab    on contacts (establishment_id);
create index if not exists ix_contact_email     on contacts (lower(nominative_email));
create index if not exists ix_contact_status    on contacts (email_status);
create index if not exists ix_contact_optout    on contacts (opt_out_at) where opt_out_at is not null;

-- -----------------------------------------------------------------------------
-- 3. Table OPT_OUT — registre central de désinscription (compliance)
--    Toute adresse ici ne doit JAMAIS être recontactée, tous projets confondus
-- -----------------------------------------------------------------------------
create table if not exists opt_out (
    id            uuid primary key default gen_random_uuid(),
    email         text not null,
    email_hash    text generated always as (encode(digest(lower(email), 'sha256'), 'hex')) stored,
    reason        text,                          -- 'unsubscribe_link' | 'manual' | 'complaint' | 'bounce'
    source        text,
    opted_out_at  timestamptz not null default now()
);

create unique index if not exists ux_optout_email on opt_out (lower(email));
create index if not exists ix_optout_hash on opt_out (email_hash);

-- -----------------------------------------------------------------------------
-- 4. Table CAMPAIGNS — campagnes d'envoi
-- -----------------------------------------------------------------------------
create table if not exists campaigns (
    id           uuid primary key default gen_random_uuid(),
    name         text not null,
    vertical     text,                           -- 'yoga' | 'pilates' | 'fitness'
    country      char(2),
    template_id  text,                           -- variante A/B
    status       text default 'draft',           -- draft | active | paused | completed
    sent_count   integer default 0,
    created_at   timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- 5. Table EMAIL_SENDS — suivi des envois et événements (tracking)
-- -----------------------------------------------------------------------------
create table if not exists email_sends (
    id            uuid primary key default gen_random_uuid(),
    contact_id    uuid references contacts(id) on delete set null,
    campaign_id   uuid references campaigns(id) on delete set null,

    sent_at       timestamptz,
    opened_at     timestamptz,
    clicked_at    timestamptz,
    replied_at    timestamptz,
    bounced       boolean default false,
    complained    boolean default false,
    registered    boolean default false,         -- inscription au WWW confirmée

    provider_msg_id text,                         -- ID message SendGrid
    created_at    timestamptz not null default now()
);

create index if not exists ix_sends_contact  on email_sends (contact_id);
create index if not exists ix_sends_campaign on email_sends (campaign_id);

-- -----------------------------------------------------------------------------
-- 6. Trigger : mise à jour automatique de updated_at
-- -----------------------------------------------------------------------------
create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_estab_updated on establishments;
create trigger trg_estab_updated before update on establishments
    for each row execute function set_updated_at();

drop trigger if exists trg_contact_updated on contacts;
create trigger trg_contact_updated before update on contacts
    for each row execute function set_updated_at();

-- -----------------------------------------------------------------------------
-- 7. Vue : contacts prêts à être contactés (filtre conformité intégré)
-- -----------------------------------------------------------------------------
create or replace view contacts_mailable as
select
    c.id            as contact_id,
    c.full_name,
    c.role,
    c.nominative_email,
    e.name          as establishment_name,
    e.category,
    e.city,
    e.state,
    e.country,
    e.website
from contacts c
join establishments e on e.id = c.establishment_id
where c.nominative_email is not null
  and c.email_status = 'valid'
  and c.opt_out_at is null
  and not exists (
      select 1 from opt_out o where o.email_hash = encode(digest(lower(c.nominative_email), 'sha256'), 'hex')
  );

-- -----------------------------------------------------------------------------
-- 8. Row Level Security (RLS)
--    Le pipeline backend utilise la "service_role" key qui bypass RLS.
--    On active RLS pour bloquer tout accès anonyme par défaut (sécurité).
-- -----------------------------------------------------------------------------
alter table establishments enable row level security;
alter table contacts        enable row level security;
alter table opt_out         enable row level security;
alter table campaigns       enable row level security;
alter table email_sends     enable row level security;

-- Aucune policy publique = aucun accès via la clé "anon".
-- Le backend (scripts Python) utilise la service_role key, non soumise à RLS.

-- =============================================================================
-- FIN DU SCHÉMA
-- =============================================================================
