# GitHub Actions — Cron d'envoi quotidien

Le workflow `.github/workflows/send-daily.yml` envoie **400 emails par jour ouvré**
(Mon-Fri, 08:00 UTC = 10:00 Bruxelles été / 09:00 hiver) jusqu'à épuisement des
drafts approuvés.

## 1. Configurer les secrets GitHub

Aller dans **Settings → Secrets and variables → Actions → Repository secrets**
sur le repo (https://github.com/martialparfait/www-prospection/settings/secrets/actions)
et créer **7 secrets** (les mêmes valeurs que dans le `.env` local) :

| Nom | Valeur |
|---|---|
| `SUPABASE_URL` | `https://nbpvxppxflpmtifuqviz.supabase.co` |
| `SUPABASE_SECRET_KEY` | `sbp_…` (voir `.env`) |
| `SENDGRID_API_KEY` | `SG.…` (voir `.env`) |
| `SENDGRID_FROM_EMAIL` | `jean-guy@world-wellness-weekend.net` |
| `SENDGRID_FROM_NAME` | `Jean-Guy de Gabriac` |
| `SENDGRID_REPLY_TO` | `jean-guy@weekend-wellness.com` |
| `SENDGRID_UNSUB_GROUP_ID` | `59502` |

> **Sécurité** : GitHub chiffre les secrets at-rest et les masque automatiquement
> dans les logs. Ils ne sont accessibles qu'aux workflows du repo.

Commande rapide (depuis `/Users/martialparfait/Claude Code/WWW Prospection`, gh CLI installé) :

```bash
# Charge le .env local et pousse chaque variable comme un secret GH Actions
set -a; source .env; set +a
for k in SUPABASE_URL SUPABASE_SECRET_KEY SENDGRID_API_KEY SENDGRID_FROM_EMAIL \
         SENDGRID_FROM_NAME SENDGRID_REPLY_TO SENDGRID_UNSUB_GROUP_ID; do
  gh secret set "$k" --body "${!k}"
done
```

## 2. Vérifier que le workflow apparaît

Après le `git push`, va sur **Actions** dans le repo. Le workflow « Send daily
emails (metro_fitness_2026) » doit apparaître dans la liste.

## 3. Premier test manuel (avant le cron auto)

Avant de laisser tourner le cron, **lance manuellement un dry-run** :

1. Onglet **Actions** → workflow « Send daily emails »
2. Bouton **Run workflow** (en haut à droite)
3. Cocher `dry_run = true`, laisser `limit = 400`
4. Lancer → suivre les logs en live

Le dry-run liste les drafts qui seraient envoyés sans les envoyer.

Si le dry-run est OK, lance un **vrai test à petite échelle** :

1. **Run workflow** → `dry_run = false`, `limit = 5`
2. Vérifier que les 5 emails arrivent + que `email_sends` se remplit + que la
   page `/stats` affiche les 5 envois

## 4. Cron automatique

Le cron tourne automatiquement à `08:00 UTC` du lundi au vendredi. Tant qu'on
est avant `2026-06-09` (date de démarrage hardcodée dans le workflow), il skip
et ne fait rien. Le premier vrai envoi cron sera donc **mardi 2026-06-09 à
10:00 CET**.

Pour avancer ou reculer la date de démarrage, modifier la ligne :
```yaml
CAMPAIGN_START_DATE: "2026-06-09"
```
dans `.github/workflows/send-daily.yml`.

## 5. Monitoring quotidien

- **Onglet Actions** : voir l'historique de tous les runs, les logs sont
  conservés 90 jours
- **Artifact `send-log-<run_id>`** : log complet du run (téléchargeable)
- **Page `/stats`** : KPI temps réel — sentToday, approvedRemaining, ETA
  recalculés à chaque chargement
- **Alertes GitHub** : tu reçois un email automatique si un run échoue

## 6. Pause / reprise

Pour **mettre en pause** la campagne :
- Soit désactiver le workflow (Actions → ⋯ → Disable workflow)
- Soit rejeter manuellement les drafts approuvés via `/drafts?status=approved`
  (ils ne seront plus picks)

Pour **reprendre** : ré-activer le workflow OU re-approuver des drafts.

## 7. Volumétrie & deliverability

| Métrique | Valeur cible | Action si dépassé |
|---|---|---|
| Bounce rate | < 2 % | Pause + investiguer la qualité d'enrichissement |
| Spam complaints | < 0.1 % | Pause IMMÉDIATE — risque de blacklist Gmail/Outlook |
| Désabonnements | < 0.5 % | Pas d'action si stable, monitorer |

Ces seuils sont monitorés sur la carte « Santé deliverability » de `/stats`.

## 8. Diagnostic en cas d'échec

| Symptôme | Cause probable | Fix |
|---|---|---|
| Run ne se déclenche pas | Schedule désactivé après inactivité (GitHub fait ça après 60j sans commit) | Faire un commit anodin pour réactiver |
| `❌ Variables .env manquantes` | Un secret n'a pas été créé | Vérifier `gh secret list` |
| `❌ HTTP 401` SendGrid | API key invalide ou révoquée | Régénérer dans SendGrid + `gh secret set SENDGRID_API_KEY` |
| `❌ HTTP 429` SendGrid | Rate limit dépassé | Le script throttle à 0.5s — vérifier qu'aucun autre process n'envoie |
| 0 emails envoyés mais run OK | 0 drafts en status=approved | Aller approuver des drafts sur `/drafts?status=draft` |
