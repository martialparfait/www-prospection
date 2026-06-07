# SendGrid — Setup pour la campagne `metro_fitness_2026`

Configuration côté SendGrid à faire **avant** le premier envoi. Sans ces étapes,
le taux de delivery sera catastrophique (< 30%) et le domaine peut être
blacklisté en 48h par les règles bulk sender Google/Microsoft (fév. 2024+).

## 1. Sender Authentication (DKIM/SPF/DMARC) — CRITIQUE

Aller dans **Settings → Sender Authentication → Authenticate Your Domain**.

1. Choisir un domaine (recommandé : `world-wellness-weekend.org` ou un sous-domaine `outreach.world-wellness-weekend.org`).
2. Choisir « Yes » à la question « Would you like to brand the links for this domain? » (link tracking sera sur ce sous-domaine).
3. SendGrid fournit 3 enregistrements CNAME → ajoute-les dans la zone DNS du domaine (chez OVH / Cloudflare / autre).
4. Attendre 5-30 min, cliquer « Verify ».
5. **Vérifier** que `dig +short s1._domainkey.<TON_DOMAINE>` renvoie bien le CNAME SendGrid.

Sans cette étape, **les emails arriveront en spam** (Gmail rejette tout sender en bulk sans DKIM aligné depuis février 2024).

## 2. Single Sender Verification

**Settings → Sender Authentication → Single Sender Verification → Create New Sender**.

- **From Name** : `Jean-Guy de Gabriac`
- **From Email Address** : `jean-guy@world-wellness-weekend.org` (ou ton alias dédié)
- **Reply To** : idem
- **Company Address** : adresse complète Tip Touch International SRL (Rue de la Loi 26, 1040 Brussels, Belgium)
- Confirmer le mail de validation reçu.

## 3. Unsubscribe Group (recommandé)

**Marketing → Unsubscribe Groups → Create New Group**.

- **Group Name** : "WWW Prospection — Wellness Industry Outreach"
- **Description** : "One-time invitation to participate in World Wellness Weekend (annual)"
- Sauvegarder, noter le **Group ID** (un nombre entier).

Ce groupe permet à SendGrid de :
- Injecter automatiquement un lien d'opt-out one-click conforme RFC 8058
- Empêcher tout futur envoi à un destinataire qui se désabonne
- Émettre un event `group_unsubscribe` vers ton webhook (qui populate `opt_out`)

## 4. API Key

**Settings → API Keys → Create API Key**.

- **Name** : "WWW Prospection sender"
- **Permissions** : "Restricted Access" → activer uniquement :
  - Mail Send : Full Access
  - Suppressions : Read Access (optionnel)
- Copier la clé `SG.xxxxxxxx...` → la mettre dans `.env` :
  ```
  SENDGRID_API_KEY=SG.xxxxxxxx...
  SENDGRID_FROM_EMAIL=jean-guy@world-wellness-weekend.org
  SENDGRID_FROM_NAME=Jean-Guy de Gabriac
  SENDGRID_REPLY_TO=jean-guy@world-wellness-weekend.org
  SENDGRID_UNSUB_GROUP_ID=12345
  ```
- **Ne JAMAIS** commit cette clé. `.env` est gitignored.

## 5. Event Webhook (pour les stats)

**Settings → Mail Settings → Event Webhook → Edit (or Create)**.

- **HTTP POST URL** : `https://www-prospection.vercel.app/api/sendgrid/webhook`
- **Events to send** :
  - ✅ Processed
  - ✅ Delivered
  - ✅ Bounced
  - ✅ Spam Reports
  - ✅ Unsubscribed
  - ✅ Group Unsubscribes
  - ✅ Clicked
  - ❌ **Opened — DÉSACTIVÉ** (politique : pas de pixel tracking, voir docs/email_template_synthesis.md)
- **Signed Event Webhook Requests** : **activer**. SendGrid affiche une « Verification Key » (clé publique ECDSA P-256) → la mettre dans Vercel :
  ```
  vercel env add SENDGRID_WEBHOOK_PUBLIC_KEY production
  # coller la clé brute (sans les BEGIN/END PEM headers — le code les ajoute)
  ```
- **Test Your Integration** → clic sur "Test" : tu dois recevoir un 200 OK depuis ton endpoint.

## 6. Suppressions list (sécurité GDPR)

**Suppressions → Global Unsubscribes → Add Suppressed Addresses** : tu peux y déposer manuellement les emails qui ont déjà fait opt-out par d'autres canaux (chat, téléphone), ils ne seront plus jamais contactés.

Pré-remplir avec l'export de la table `opt_out` Supabase (vide pour l'instant).

## 7. Dedicated IP (optionnel, recommandé > 5000/mois)

Pour la campagne `metro_fitness_2026` (~1500 emails one-shot), pas indispensable. Tu peux rester sur l'IP partagée SendGrid. Si tu prévois de récurrer (campagnes annuelles), envisage un Dedicated IP + warmup progressif.

---

## Variables d'environnement nécessaires

### Côté script Python (`.env` à la racine)

```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=jean-guy@world-wellness-weekend.org
SENDGRID_FROM_NAME=Jean-Guy de Gabriac
SENDGRID_REPLY_TO=jean-guy@world-wellness-weekend.org
SENDGRID_UNSUB_GROUP_ID=12345  # optionnel mais recommandé
```

### Côté Vercel (interface web) — via `vercel env add`

```bash
vercel env add SENDGRID_WEBHOOK_PUBLIC_KEY production
# colle la clé publique du webhook (depuis Settings → Mail Settings → Event Webhook)
```

---

## Premier test (sécurisé)

Une fois tout configuré :

```bash
# 1. Test deliverability vers TON adresse perso
python3 send_drafts.py --test toi@yourdomain.com

# Ouvre l'email reçu, clique sur le bouton CTA → vérifie que :
#   - L'email arrive en INBOX (pas spam)
#   - DKIM/SPF/DMARC : 3 PASS dans les headers
#   - Le clic est trackée → check /stats sur l'interface après ~30 sec
```

Si tout est OK :

```bash
# 2. Sample réel (1 destinataire, depuis les drafts approuvés)
python3 send_drafts.py --status approved --limit 1

# 3. Si OK : lance les drafts approuvés restants
python3 send_drafts.py --status approved
```

---

## Checklist avant le premier envoi

- [ ] DKIM/SPF/DMARC verified (`dig +short` confirme les CNAME)
- [ ] Sender single verified (mail de Jean-Guy reçu et cliqué)
- [ ] Unsubscribe Group créé et `SENDGRID_UNSUB_GROUP_ID` dans `.env`
- [ ] API Key dans `.env` (Mail Send full access uniquement)
- [ ] Event Webhook configuré, URL pointe sur Vercel prod, signature **activée**
- [ ] `SENDGRID_WEBHOOK_PUBLIC_KEY` dans Vercel env vars
- [ ] Page `/stats` accessible et affiche "Aucun envoi pour l'instant"
- [ ] Test à mon adresse perso passé (inbox + clic tracké)
- [ ] Drafts en status `approved` (via la page `/drafts` une fois le workflow d'approbation en place — Phase B)
