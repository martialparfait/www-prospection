# wellmap.org → WWW Prospection — Webhook de conversion

Ce document est destiné au **dev qui maintient wellmap.org** (`map.world-wellness-weekend.org`).
Il décrit l'intégration à monter pour qu'on puisse mesurer combien d'inscriptions
viennent de chaque email envoyé par la campagne `metro_fitness_2026`.

## Pourquoi

Les emails sortants contiennent un bouton CTA dont l'URL inclut un paramètre
`utm_content={draft_id}` (UUID) unique par destinataire. Quand un utilisateur
clique sur le bouton et complète son inscription sur wellmap.org, on a besoin
que wellmap **renvoie ce `draft_id`** à notre infra pour le matcher au bon
contact côté Supabase et compter la conversion.

Sans ça, on sait juste « X personnes ont cliqué » mais pas « Y personnes se sont
réellement inscrites grâce à l'email Z ».

## Architecture

```
[Email] → clic CTA  → wellmap landing  → tunnel signup → signup complété
              │            │                                  │
              │     stocke utm_* en                            │
              │     cookie www_attrib                          │
              │                                                ▼
              │                                  POST https://www-prospection.vercel.app/api/conversions
              │                                  Header: X-WWW-Token: <secret partagé>
              │                                  Body: { draft_id, email, registered_at, campaign?, subject_variant? }
```

## À implémenter côté wellmap.org

### 1. Capturer les UTMs au landing (JavaScript, toutes les pages d'entrée)

À placer dans le `<head>` du thème, ou via Google Tag Manager si déjà présent :

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

Cookie `www_attrib` valable 30 jours, `Secure`, `SameSite=Lax`.

### 2. POST vers `/api/conversions` au moment du signup (côté serveur)

#### Si le site est WordPress (cas le plus probable d'après `wp-content` dans le path) :

```php
// dans functions.php ou un mu-plugin — exécuté quand WordPress crée un nouveau compte
add_action('user_register', function($user_id) {
    if (empty($_COOKIE['www_attrib'])) return;
    $attrib = json_decode(stripslashes($_COOKIE['www_attrib']), true);
    if (empty($attrib['utm_content'])) return;  // pas un lead campagne — on ignore

    $user = get_userdata($user_id);

    $resp = wp_remote_post('https://www-prospection.vercel.app/api/conversions', [
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
        'blocking' => false,  // fire-and-forget : ne pas bloquer le signup user
    ]);

    // Nettoyage du cookie après usage (évite ré-envois sur d'autres comptes du même device)
    setcookie('www_attrib', '', time() - 3600, '/', '', true, false);
});
```

Stocker le secret dans `wp-config.php` (jamais dans le code commité) :

```php
define('WWW_CONVERSIONS_TOKEN', '••••••••');  // → demander la valeur à Martial
```

#### Si le site n'est pas WordPress

Hooker l'évènement « compte créé » dans le framework backend (Laravel `User::created`,
Node `user.create` event…) et faire le même POST. Le payload et le header sont
identiques.

## Contrat du payload

`POST https://www-prospection.vercel.app/api/conversions`

**Headers :**
- `Content-Type: application/json`
- `X-WWW-Token: <secret partagé>` — fourni hors-bande par Martial

**Body JSON :**
```json
{
  "draft_id": "7b7083ba-1f0a-486c-bde7-199c7678feff",
  "email": "user@example.com",
  "registered_at": "2026-06-08T10:34:11Z",
  "campaign": "metro_fitness_2026",
  "subject_variant": "A"
}
```

| Champ | Type | Requis | Source |
|---|---|---|---|
| `draft_id` | UUID v4 | ✅ | `utm_content` du cookie |
| `email` | string | ✅ | adresse de signup |
| `registered_at` | ISO 8601 | ❌ (default: now) | date de création du compte |
| `campaign` | string | ❌ | `utm_campaign` du cookie |
| `subject_variant` | string (A/B/C/D/E) | ❌ | `utm_term` du cookie |

## Réponses possibles

| Status | Body | Signification |
|---|---|---|
| `200` | `{ "ok": true, "matched_send": true }` | Conversion enregistrée et matchée à un envoi connu |
| `200` | `{ "ok": true, "matched_send": false }` | Enregistrée (audit) mais pas de send matchant — log côté Vercel |
| `400` | `{ "ok": false, "error": "..." }` | Payload invalide (UUID malformé, email manquant) |
| `401` | `Unauthorized` | Token absent/incorrect |
| `503` | `{ "error": "Server not configured" }` | Variable `WWW_CONVERSIONS_TOKEN` absente côté Vercel |

## Test rapide (avant mise en prod)

Healthcheck (ne nécessite pas le token) :
```bash
curl https://www-prospection.vercel.app/api/conversions
# → { "ok": true, "service": "...", "auth_configured": true }
```

Test d'un POST avec un UUID bidon :
```bash
curl -X POST https://www-prospection.vercel.app/api/conversions \
  -H "Content-Type: application/json" \
  -H "X-WWW-Token: $WWW_CONVERSIONS_TOKEN" \
  -d '{
    "draft_id": "00000000-0000-0000-0000-000000000000",
    "email": "test@example.com",
    "registered_at": "2026-06-08T10:34:11Z"
  }'
# → { "ok": true, "matched_send": false }   (pas de send matchant — normal pour ce UUID bidon)
```

Si tu reçois `200`, l'intégration est OK. Le `matched_send: false` est attendu
ici (ce UUID n'existe pas en base) — en prod avec un vrai `utm_content`, ça
basculera à `true` et la conversion apparaîtra dans le dashboard
`/stats` côté Martial.

## Côté Vercel (info — déjà fait par Martial)

- Endpoint : `web/src/app/api/conversions/route.ts`
- Variable d'env : `WWW_CONVERSIONS_TOKEN` (Vercel project settings → Environment Variables → Production)
- Table audit : `email_conversions` Supabase
- Mise à jour : `email_sends.registered_at` + `email_sends.registered_email`
