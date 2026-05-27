# WWW Prospection — Interface de consultation

Interface web (lecture seule) pour parcourir les établissements et contacts
collectés pour **World Wellness Weekend**. Destinée à toi et au client.

- **Stack** : Next.js 16 (App Router) · Supabase (côté serveur) · Tailwind CSS.
- **Accès** : protégé par un mot de passe partagé.
- **Données** : lues en direct depuis Supabase avec la clé secrète (jamais exposée
  au navigateur). Le RLS reste actif ; tout passe par le serveur.

## Pages

| Route | Contenu |
|---|---|
| `/login` | Saisie du mot de passe. |
| `/` | Tableau de bord : volumes, avancement de l'enrichissement, qualité des emails, top États, sources. |
| `/establishments` | Liste filtrable/triable (recherche, catégorie, État, statut) avec pagination. |
| `/establishments/[id]` | Fiche détaillée + contacts identifiés (email, rôle, source, vérification). |

## Lancer en local

```bash
cd web
cp .env.example .env.local   # puis renseigner les valeurs
npm install
npm run dev                  # http://localhost:3000
```

Variables d'environnement (voir `.env.example`) :

| Variable | Rôle |
|---|---|
| `SUPABASE_URL` | URL du projet Supabase. |
| `SUPABASE_SECRET_KEY` | Clé secrète (service role), **serveur uniquement**. |
| `APP_PASSWORD` | Mot de passe d'accès partagé. |
| `AUTH_SECRET` | Secret aléatoire pour signer le cookie de session (`openssl rand -hex 32`). |

## Déploiement Vercel

```bash
cd web
vercel            # 1er run : lie le projet (login requis)
# Renseigner les 4 variables d'env dans le dashboard Vercel
# (Project → Settings → Environment Variables), pour Production & Preview.
vercel --prod     # déploiement production
```

> Les variables d'env **ne sont pas** poussées automatiquement : il faut les
> ajouter côté Vercel (ou `vercel env add`). Ne jamais committer `.env.local`.

## Sécurité

- La clé secrète Supabase n'est utilisée que dans les composants serveur
  (`src/lib/supabase.ts`, marqué `server-only`).
- Le `proxy.ts` fait un contrôle d'accès optimiste ; la vérification réelle du
  cookie (HMAC) est faite dans `src/app/(app)/layout.tsx`.
- L'app est en `noindex` (pas d'indexation moteur).
