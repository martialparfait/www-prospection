# Prochaines étapes — Tracking des conversions

Pour mesurer le funnel **email envoyé → clic → inscription effective sur wellmap.org**,
deux moitiés à câbler : une côté **WordPress (wellmap.org)** et une côté **notre infra**.

---

## A. Côté WordPress (wellmap.org) — à confier au dev WP

Le but : quand un visiteur arrive depuis un email de la campagne, on capture les
UTMs en cookie, puis quand il crée son compte, WordPress envoie un POST à notre
endpoint avec son `draft_id` pour qu'on puisse l'attribuer.

### 1. Snippet JS sur toutes les pages d'entrée (capture des UTMs)

À ajouter dans le `<head>` du thème actif, ou via Google Tag Manager s'il est en place :

```html
<script>
(function() {
  var params = new URLSearchParams(window.location.search);
  var utms = {};
  ['utm_source','utm_medium','utm_campaign','utm_content','utm_term']
    .forEach(function(k) { if (params.has(k)) utms[k] = params.get(k); });
  if (Object.keys(utms).length) {
    utms._captured_at = new Date().toISOString();
    document.cookie = 'www_attrib=' + encodeURIComponent(JSON.stringify(utms)) +
                      ';path=/;max-age=2592000;SameSite=Lax;Secure';
  }
})();
</script>
```

Le cookie `www_attrib` dure 30 jours et survit au tunnel d'inscription.

### 2. Hook PHP qui poste vers notre endpoint au signup

À placer dans `functions.php` du thème (ou mieux : un mu-plugin dédié) :

```php
add_action('user_register', function($user_id) {
    if (empty($_COOKIE['www_attrib'])) return;
    $attrib = json_decode(stripslashes($_COOKIE['www_attrib']), true);
    if (empty($attrib['utm_content'])) return;  // pas un lead campagne

    $user = get_userdata($user_id);
    wp_remote_post('https://www-prospection.vercel.app/api/conversions', [
        'headers' => [
            'Content-Type' => 'application/json',
            'X-WWW-Token'  => defined('WWW_CONVERSIONS_TOKEN') ? WWW_CONVERSIONS_TOKEN : '',
        ],
        'body' => wp_json_encode([
            'draft_id'        => $attrib['utm_content'],
            'email'           => $user->user_email,
            'registered_at'   => mysql2date('c', $user->user_registered),
            'campaign'        => $attrib['utm_campaign'] ?? null,
            'subject_variant' => $attrib['utm_term'] ?? null,
        ]),
        'timeout' => 5,
        'blocking' => false,  // fire-and-forget, ne bloque pas l'UX signup
    ]);
    // Cleanup cookie après usage
    setcookie('www_attrib', '', time() - 3600, '/', '', true, false);
});
```

### 3. Secret à mettre dans `wp-config.php`

```php
define('WWW_CONVERSIONS_TOKEN', '<TOKEN_PARTAGÉ_FOURNI_PAR_MARTIAL>');
```

Le token est à demander à Martial **hors-bande** (Signal, 1Password, etc.) —
**jamais par email ou dans le code commité**.

### 4. Tests à faire côté WordPress (avant prod)

```bash
# 1. Healthcheck depuis le serveur WP
curl https://www-prospection.vercel.app/api/conversions
# → { "ok": true, "service": "...", "auth_configured": true }

# 2. POST avec un UUID bidon pour valider l'auth
curl -X POST https://www-prospection.vercel.app/api/conversions \
  -H "Content-Type: application/json" \
  -H "X-WWW-Token: $WWW_CONVERSIONS_TOKEN" \
  -d '{
    "draft_id": "00000000-0000-0000-0000-000000000000",
    "email": "test@example.com",
    "registered_at": "2026-06-07T10:00:00Z"
  }'
# → { "ok": true, "matched_send": false }
```

Si tu reçois 200 OK → l'intégration est fonctionnelle.

### 5. Validation end-to-end

1. Cliquer sur le bouton CTA d'un email reçu de la campagne (utm_content présent)
2. Atterrir sur wellmap.org → vérifier qu'un cookie `www_attrib` est créé (DevTools → Application → Cookies)
3. Créer un compte test
4. Vérifier dans `email_conversions` Supabase qu'une ligne a été insérée
5. Vérifier sur `/stats` que la KPI **"Inscriptions"** est passée à 1

---

## B. Côté nous (Vercel + Supabase) — déjà fait

| Item | Statut |
|---|---|
| Migration Supabase (`email_sends.registered_at`, table `email_conversions`) | ✅ Appliquée |
| Endpoint `POST /api/conversions` (auth X-WWW-Token timing-safe) | ✅ Déployé |
| Endpoint `GET /api/conversions` (healthcheck) | ✅ Déployé |
| Matcher proxy exclu `/api/conversions` | ✅ Fait |
| UTM `utm_content={draft_id}` injecté dans chaque CTA email | ✅ Fait (1438 drafts régénérés) |
| Page `/stats` avec carte funnel + KPI Inscriptions | ✅ Déployée |
| Token `WWW_CONVERSIONS_TOKEN` poussé dans Vercel env vars | ⏳ **À faire** par Martial |

### Action restante côté Vercel

Une seule commande :

```bash
cd "/Users/martialparfait/Claude Code/WWW Prospection/web"
vercel env add WWW_CONVERSIONS_TOKEN production
# coller : vP7ZQqPVBc7ipOi5jcp7VgO9Wcx0dwW-O48V8UBTz58xKgf_fXf5Vv0YaIvCflvs
vercel --prod  # redeploy pour que la nouvelle env soit lue
```

Sans cette étape, l'endpoint répondra `503 Server not configured` et WordPress
recevra une erreur quand il essaiera de poster.

### Comment vérifier que tout est OK

```bash
curl https://www-prospection.vercel.app/api/conversions
# Doit renvoyer : { "ok": true, "service": "...", "auth_configured": true }
#                                                  ↑ doit être true
```

---

## C. Ce qui se passe ensuite (le funnel complet)

```
1. Cron envoie un email (avec utm_content={draft_id_X} dans la CTA)
        ↓
2. Destinataire clique → SendGrid trace le clic → webhook /api/sendgrid/webhook
   → email_sends.clicked_at = NOW(), click_count++
        ↓
3. Atterrit sur wellmap.org → JS capture les UTMs en cookie www_attrib
        ↓
4. Visite éventuellement plusieurs pages, ferme l'onglet, revient plus tard
   (le cookie survit 30j)
        ↓
5. Crée son compte → hook PHP user_register → POST /api/conversions
        ↓
6. Notre endpoint matche utm_content au draft_id, met à jour
   email_sends.registered_at = NOW() + email_sends.registered = true
   + insère une ligne email_conversions pour l'audit
        ↓
7. La page /stats affiche : envoyés / clics / inscriptions + funnel + ETA
   + classement par variant A/B/C/D/E → on sait quel angle convertit
```

Tu as alors **3 niveaux de mesure** :

| Métrique | Source | Précision |
|---|---|---|
| Délivery / bounce / unsub | Webhook SendGrid | Live |
| Clic | Webhook SendGrid (click_count) | Live |
| Inscription | POST /api/conversions depuis wellmap | Live |

---

## D. Si le dev wellmap traîne ou refuse

Plan B : **export hebdomadaire manuel**.

Le dev wellmap nous envoie chaque vendredi un CSV de tous les nouveaux comptes
créés depuis le lundi (email + date). On fait un JOIN SQL avec
`email_sends.recipient_email` côté Supabase pour identifier qui s'est inscrit.

C'est moins précis (pas d'attribution exacte au draft_id si l'utilisateur s'inscrit
avec un email différent de celui ciblé), mais ça donne le **gros chiffre** :
combien de comptes créés viennent de la campagne.

À demander au dev wellmap si l'intégration full live n'est pas faisable
rapidement.
