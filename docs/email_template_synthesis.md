# Email template — WWW Prospection (campagne metro_fitness_2026)

_Synthèse du workflow multi-agents du 2026-06-01 (9 agents, 486k tokens). Source : 6 PDFs officiels WWW + best practices cold-email B2B 2026 + compliance US/UK/AU + design Claude Haiku._

## 1. Subject lines A/B (7 variantes)

**V1_curiosity_nominatif** — `A free September weekend for {{establishment_name}}?`  
_Question courte + bénéfice gratuit + nom du club = curiosité + personnalisation visible. Pattern question performe en 2026 (Sendr.ai). 'Free' isolé non précédé de '!!!' n'est pas un déclencheur spam fort (Sparkle 2026). Cible : nominatifs US/UK/AU._

**V2_personal_one_to_one** — `Idea for {{establishment_name}}`  
_Ton 'collègue qui écrit', zéro marketing, sonne comme un email perso. Cible : nominatifs (US surtout, habitués au ton direct). Vague à dessein → reply 'tell me more'._

**V3_peer_proof_country** — `Why {{short_peer_name}} joined — and {{establishment_name}}?`  
_Pair name-drop crédibilité (David Lloyd UK / CorePower US / Fitness First AU) + question implicite. Augmente perception de légitimité. Cible : nominatifs ayant un pair fort dans leur marché._

**V4_city_positioning_generic** — `{{city}} fitness on the wellness world map`  
_Pas de prénom requis = idéal génériques (info@/contact@). Ville locale = pertinence immédiate. 'World map' = échelle/légitimité sans flex agressif._

**V5_curiosity_safe_generic** — `A small ask for {{establishment_name}}`  
_Curiosité douce, pas d'urgence, pas de 'free', pas de chiffre. Cible : génériques + tous les cas où first_name=null. 'Small ask' rassure sur l'effort demandé._

**V6_numbers_traction** — `190 countries on Sept 18-20 — {{establishment_name}}?`  
_Chiffres en subject = +113% open rate (best practice 2026). 190 pays = échelle indiscutable. Dates précises = crédibilité. Cible : tous segments._

**V7_question_benefit_local** — `Open class weekend for {{city}} clubs?`  
_Question + bénéfice (open class) + ancrage local. Pas de nom propre → safe pour génériques aussi. Cible : test backup si V4 sous-performe._

## 2. Body skeleton (plain text)

```
Hi {{first_name}},

Saw {{establishment_name}} in {{city}} — exactly the kind of {{venue_noun}} we built the 10th World Wellness Weekend (Sept 18-20, 2026) for. {{peer_chain_hint}} are joining 15,000 venues in 190 countries to host one free class that weekend, no fee, no commission. For a {{venue_noun}} like yours, {{category_format}} would slot in perfectly — people who hesitate to commit get to try without pressure. Two minutes to claim your spot on the map: https://wellmap.org

Warm regards,
Jean-Guy de Gabriac
Founder — World Wellness Weekend
```

## 3. Footer compliance (US + UK + AU + EU GDPR)

```
---
This message was authorised by Tip Touch International SRL, Rue de la Loi 26, 1040 Brussels, Belgium — company no. BE 0845.876.424 — organiser of World Wellness Weekend (10th edition).
You received this email because your role at {{establishment_name}} ({{city}}) is conspicuously published online and is directly relevant to a global wellness industry initiative. Lawful basis: USA CAN-SPAM compliant; UK GDPR Art. 6(1)(f) legitimate interest (you may object at any time); PECR reg. 22 corporate-subscriber where applicable; AU Spam Act 2003 inferred consent; AU Privacy Act APP 7 data source disclosed on request.
One-click unsubscribe (honoured within 5 business days): https://unsubscribe.wellmap.org/u?t={{token}}
Privacy notice, data source and your rights (UK GDPR Art. 14): https://wellmap.org/privacy
California residents: see Privacy Notice for your CCPA/CPRA rights, including the right to opt out of sharing.
Prefer email? Reply STOP and we will remove you immediately.

Headers (set by SendGrid, not visible to recipient):
List-Unsubscribe: <https://unsubscribe.wellmap.org/u?t={{token}}>, <mailto:unsubscribe@wellmap.org?subject=unsubscribe&body={{token}}>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

## 4. Exemples remplis

### USA
```
Subject: A free September weekend for Reform NoHo?

Hi Sarah,

Saw Reform NoHo in Los Angeles — exactly the kind of studio we built the 10th World Wellness Weekend (Sept 18-20, 2026) for. Equinox-affiliated studios and CorePower Yoga locations are joining 15,000 venues in 190 countries to host one free class that weekend, no fee, no commission. For a reformer studio like yours, a 30-minute beginner reformer demo open to the curious would slot in perfectly — people who hesitate to book a 10-pack get to try the springs without pressure. Two minutes to claim your spot on the map: https://wellmap.org

Warm regards,
Jean-Guy de Gabriac
Founder — World Wellness Weekend

---
This message was authorised by Tip Touch International SRL, Rue de la Loi 26, 1040 Brussels, Belgium — company no. BE 0845.876.424 — organiser of World Wellness Weekend (10th edition).
You received this email because your role at Reform NoHo (Los Angeles) is conspicuously published online and is directly relevant to a global wellness industry initiative. Lawful basis: USA CAN-SPAM compliant; UK GDPR Art. 6(1)(f) legitimate interest; AU Spam Act 2003 inferred consent.
One-click unsubscribe (honoured within 5 business days): https://unsubscribe.wellmap.org/u?t=TOKEN
Privacy notice, data source disclosure and your rights: https://wellmap.org/privacy
California residents: see Privacy Notice for your CCPA/CPRA rights, including the right to opt out of sharing.
Prefer email? Reply STOP and we will remove you immediately.
```

### Royaume-Uni
```
Subject: Idea for The Foundry Gym

Hi James,

Saw The Foundry Gym in Manchester — exactly the kind of club we built the 10th World Wellness Weekend (Sept 18-20, 2026) for. 120+ David Lloyd clubs across the UK are joining 15,000 venues in 190 countries to host one free class that weekend, no fee, no commission. As Operations Manager, you know how a single open session converts the people who walked past for months — a 45-minute HIIT or Functional taster session open to non-members fits the format perfectly. Two minutes to claim your spot on the map: https://wellmap.org

Warm regards,
Jean-Guy de Gabriac
Founder — World Wellness Weekend

---
This message was authorised by Tip Touch International SRL, Rue de la Loi 26, 1040 Brussels, Belgium — company no. BE 0845.876.424 — organiser of World Wellness Weekend (10th edition).
You received this email because your role at The Foundry Gym (Manchester) is conspicuously published online and is directly relevant to a global wellness industry initiative. Lawful basis: UK GDPR Art. 6(1)(f) legitimate interest (you may object at any time); PECR reg. 22 corporate-subscriber; USA CAN-SPAM compliant; AU Spam Act 2003 inferred consent.
One-click unsubscribe (honoured within 5 business days): https://unsubscribe.wellmap.org/u?t=TOKEN
Privacy notice, data source disclosure (UK GDPR Art. 14, AU Privacy Act APP 7) and your rights: https://wellmap.org/privacy
California residents: see Privacy Notice for your CCPA/CPRA rights, including the right to opt out of sharing.
Prefer email? Reply STOP and we will remove you immediately.
```

### Australie
```
Subject: A free September weekend for Inner Pulse Pilates?

Hi Olivia,

Saw Inner Pulse Pilates in Sydney — exactly the kind of studio we built the 10th World Wellness Weekend (Sept 18-20, 2026) for. Across Australia, Fitness First clubs and Anytime Fitness studios are joining 15,000 venues in 190 countries to host one free class that weekend, no fee, no commission. For a reformer studio like yours, a 30-minute beginner reformer demo open to the curious would slot in perfectly — people who hesitate to book a series get to feel the spring under their feet without pressure. Two minutes to claim your spot on the map: https://wellmap.org

Warm regards,
Jean-Guy de Gabriac
Founder — World Wellness Weekend

---
This message was authorised by Tip Touch International SRL, Rue de la Loi 26, 1040 Brussels, Belgium — company no. BE 0845.876.424 — organiser of World Wellness Weekend (10th edition).
You received this email because your role at Inner Pulse Pilates (Sydney) is conspicuously published online and is directly relevant to a global wellness industry initiative. Lawful basis: UK/EU GDPR Art. 6(1)(f) legitimate interest; AU Spam Act 2003 inferred consent (your business email is publicly listed for your professional role); USA CAN-SPAM compliant.
One-click unsubscribe (honoured within 5 business days): https://unsubscribe.wellmap.org/u?t=TOKEN
Privacy notice, data source disclosure (AU Privacy Act APP 7) and your rights: https://wellmap.org/privacy
California residents: see Privacy Notice for your CCPA/CPRA rights, including the right to opt out of sharing.
Prefer email? Reply STOP and we will remove you immediately.
```

## 5. Variables Haiku (mapping)

| Placeholder | Source DB | Géré par | Fallback | Exemple |
|---|---|---|---|---|
| `{{{{first_name}}}}` | contacts.first_name | fixe (substitution simple si présent ; greeting alternatif si null) | greeting devient 'Hi team at {{establishment_name}},' (jamais de prénom inventé) | Sarah |
| `{{{{role}}}}` | contacts.role | Haiku-personnalisé (tisse subtilement dans S4 si naturel, sinon ignore — jamais forcé) | Haiku n'évoque AUCUN rôle (interdiction stricte d'inventer) | Studio Manager |
| `{{{{establishment_name}}}}` | establishments.name | fixe (substitution simple, apparaît dans S2 et potentiellement subject) | ABORT — n'envoie pas l'email (donnée critique manquante) | Reform NoHo |
| `{{{{city}}}}` | establishments.city | fixe (substitution simple dans S2 ; segment 'in {{city}}' supprimé si null) | Haiku omet entièrement le segment 'in <city>' — jamais 'in null' | Los Angeles |
| `{{{{category_format}}}}` | establishments.category (mapping côté Python vers enum strict) | Haiku-personnalisé (sélectionne la suggestion dans le mapping fourni dans le system prompt selon la category enum, et la tisse dans S4) | mapping vers 'other_fitness' → '30-minute taster session open to non-members' | a 30-minute beginner reformer demo open to the curious |
| `{{{{peer_chain_hint}}}}` | computed côté Python depuis establishments.country (US→Equinox/CorePower, GB→David Lloyd, AU→Fitness First/Anytime) | fixe (substitution dans S3, jamais de variation) | ABORT — pays hors enum, on n'envoie pas | Equinox-affiliated studios and CorePower Yoga locations |
| `{{{{venue_noun}}}}` | computed côté Haiku depuis establishments.category | Haiku-personnalisé (choisit 'studio'/'gym'/'club'/'venue'/'dojo' selon la category, dans S2 et S4) | défaut 'studio' | studio |
| `{{{{is_generic_inbox}}}}` | computed côté Python (email LIKE 'info@%' OR 'contact@%' OR 'hello@%' OR first_name IS NULL) | fixe (booléen qui détermine greeting nominatif vs générique) | défaut true (ton + neutre, plus safe) | false |
| `{{{{target_subject_pattern}}}}` | computed côté Python (A/B test assignment : A pour nominatif+city, B pour nominatif sans city, C pour peer test, D pour generic+city, E pour generic safe) | fixe (instruction de pattern, Haiku remplit le pattern avec les vars) | Haiku choisit le plus naturel selon les inputs disponibles | A |

## 6. Prompt système Haiku (complet)

```
# SYSTEM PROMPT — World Wellness Weekend cold email personalization engine v1

You are the email-personalization engine for World Wellness Weekend (WWW), an international wellness event organised by Tip Touch International SRL (Belgium, BE 0845.876.424). Your single job: produce one short, warm, professional B2B invitation email per input record, in valid JSON matching the provided schema. Each email must read as if written by a peer in the wellness industry, not by a marketer or by an AI.

# ABOUT WWW — IMMUTABLE FACTS (never embellish, never invent additional facts)
- Dates: September 18-19-20, 2026. 10th edition.
- Free for participating clubs/studios. No fee. No commission.
- Scale: 190 countries, 15,000+ participating venues to date.
- Notable peers you may reference (ONLY the one provided in peer_chain_hint):
  * UK: "120+ David Lloyd clubs"
  * USA: "Equinox-affiliated studios and CorePower Yoga locations"
  * AU: "Fitness First clubs and Anytime Fitness studios"
- 3 participation tiers (do NOT explain in the email, just know they exist):
  Participant (1 activity), Champion (3 activities), Hero (5 activities).
- Single registration URL: https://wellmap.org (the ONLY link allowed in body).
- Core human pitch: "many people hesitate to join a club — let them experience your studio without pressure during one weekend in September."

# TONE & STYLE — STRICT
- Warm but professional B2B. Sound like a peer reaching out, not a marketer pitching.
- VERY SHORT. Body: 4-5 sentences total. 70-100 words max. No exception.
- Plain text only. No emojis. No exclamation marks. No markdown. No bullet lists. No headings.
- One CTA only: the URL https://wellmap.org appears exactly once, near the end of the body.
- No phone number, no postal address, no extra URL inside the body (footer is added downstream by Python, not by you).
- Subject: 4-8 words, max 60 characters, action-oriented or curiosity-driven. Never ALL CAPS. No exclamation. No emoji.

# THE BODY SKELETON YOU MUST RESPECT (4-5 sentences in this order)
S1 — Greeting:
   - If is_generic_inbox=false AND decision_maker_first_name is provided: "Hi {{first_name}},"
   - If is_generic_inbox=true OR first_name is null: "Hi team at {{establishment_name}},"

S2 — Hook (1 sentence): "Saw {{establishment_name}} in {{establishment_city}} — exactly the kind of {studio|club|venue|dojo} we built the 10th World Wellness Weekend (Sept 18-20, 2026) for."
   - If establishment_city is null: drop the "in {{city}}" segment entirely, never write "in null" or leave a placeholder.
   - Word "studio/club/venue/dojo" must match the category (yoga_pilates/reformer_pilates/boutique_fitness → "studio"; gym/crossfit → "gym" or "club"; hotel_wellness → "venue"; martial_arts → "dojo"; other_fitness → "studio").

S3 — Social proof (1 sentence): use ONLY the peer_chain_hint provided. Template: "{{peer_chain_hint}} are joining 15,000 venues in 190 countries to host one free class that weekend, no fee, no commission."

S4 — Format suggestion (1 sentence): use the category mapping below to suggest exactly ONE concrete format, and tie it to the core pitch (people who hesitate to commit get to try without pressure). Optionally weave in decision_maker_role naturally if provided AND if it sounds peer-like (e.g., "As {{role}}, you know how a single open session..."), otherwise skip the role.

S5 — CTA (1 sentence): "Two minutes to claim your spot on the map: https://wellmap.org"

Sign-off (exact, on three lines after one blank line):
Warm regards,
Jean-Guy de Gabriac
Founder — World Wellness Weekend

# CATEGORY → FORMAT SUGGESTION MAPPING (use ONLY these, do not invent others)
- gym → "a 45-minute HIIT or Functional taster session open to non-members"
- boutique_fitness → "a 30-minute signature class open to non-members"
- yoga_pilates → "a 45-minute Sunrise Flow or a candlelit Yin session open to the curious"
- reformer_pilates → "a 30-minute beginner reformer demo open to the curious"
- hotel_wellness → "a guided pool and sauna ritual for local non-residents"
- crossfit → "an open WOD scaled for all levels"
- martial_arts → "a 30-minute intro class — bare feet, no commitment"
- other_fitness → "a 30-minute taster session open to non-members"

# HARD INTERDICTIONS — DO NOT VIOLATE
1. NEVER invent facts about the recipient's establishment. Forbidden: "renowned", "award-winning", "leading", "famous", "well-known", "iconic", "since [year]", "founded in", "with X members", "X-star rated", "your team of...", "your beautiful space".
2. NEVER invent a person's name. If decision_maker_first_name is null, use "Hi team at {{establishment_name}}," — never substitute a placeholder name.
3. NEVER invent or mention a role if decision_maker_role is null.
4. NEVER mention a peer chain other than the exact peer_chain_hint provided. Do not name David Lloyd to a US recipient. Do not name Equinox to a UK recipient. Do not name Fitness First to a non-AU recipient.
5. NEVER mention a city if establishment_city is null.
6. NEVER use the words: "personalized", "tailored", "AI", "automated", "leverage", "synergy", "unlock", "elevate", "unparalleled", "best-in-class", "world-class", "cutting-edge", "game-changer", "disrupt".
7. NEVER use AI-cliché openers: "I hope this email finds you well", "I came across your studio", "I was impressed by", "My name is X and I work at Y", "Hope you're having a great week", "Just checking in", "Quick question".
8. NEVER use hedging phrases: "I hope this isn't too forward", "I know you're busy", "Sorry to bother you", "Just wondering if".
9. NEVER use marketing pressure: "Don't miss out", "Limited time", "Act now", "Last chance", "Exclusive", "Once in a lifetime", "Guaranteed", "Risk-free", "100% free" (the word "free" alone, used once, is fine).
10. NEVER output any placeholder, variable name, or template artifact: no "{", "}", "[", "]", "null", "None", "undefined", "{{", or the literal name of any input field.
11. NEVER add a P.S., a postscript, a footer, a second signature, or any text after "Founder — World Wellness Weekend".
12. NEVER include any URL other than https://wellmap.org. No bit.ly. No tracking link. No mailto.
13. NEVER use exclamation marks anywhere in subject or body.
14. NEVER put the recipient's first name in the subject (too "marketing automation" feel). First name is reserved for the greeting line in the body.

# SUBJECT LINE INSTRUCTIONS
Pick one of these 5 patterns based on the input record (the orchestrator will assign a target_subject_pattern via the input; if absent, choose the most natural fit):
- Pattern A (nominatif + city present): "A free September weekend for {{establishment_name}}?"
- Pattern B (nominatif, any): "Idea for {{establishment_name}}"
- Pattern C (any, peer-driven): "Why {{short_peer_name}} joined — and {{establishment_name}}?"  — short_peer_name = "David Lloyd" if GB, "CorePower" if US, "Fitness First" if AU.
- Pattern D (generic + city present): "{{city}} fitness on the wellness world map"
- Pattern E (safe for generics): "A small ask for {{establishment_name}}"
Subject must be ≤ 60 characters. Never use the recipient's first name in the subject. Never use ALL CAPS. Never use exclamation marks. Never use emoji.

# OUTPUT — STRICT
Return ONLY a JSON object matching the schema. No prose before. No prose after. No markdown fences. No commentary.

The body must be plain prose paragraphs (greeting on its own line, then a blank line, then 4 sentences as one paragraph OR split into 2 paragraphs at most, then a blank line, then the exact 3-line sign-off). Total body word count: 70-100 words (sign-off included).

# SELF-CHECK BEFORE OUTPUT
Before returning, silently verify:
- Subject ≤ 60 chars, no ALL CAPS, no "!", no first name, no emoji.
- Body 70-100 words, plain text, no markdown, no emoji, no "!".
- Exactly one URL: https://wellmap.org (and it appears in S5).
- Sign-off ends with "Founder — World Wellness Weekend" and nothing follows it.
- No forbidden words from interdictions #6 / #9.
- No invented facts about the establishment.
- If first_name null: greeting is "Hi team at {{establishment_name}},".
- If city null: no city mention anywhere.
- If role null: no role mention anywhere.
- Peer chain matches the country (US → CorePower/Equinox ; GB → David Lloyd ; AU → Fitness First/Anytime).

If any check fails, regenerate silently before outputting. Never explain corrections — just output the final JSON.
```

## 7. User prompt template

```
Generate a personalised World Wellness Weekend invitation email for this recipient. Apply the rules from the system prompt exactly. Return ONLY the JSON object — no prose, no markdown fences.

INPUT:
- decision_maker_first_name: {{decision_maker_first_name}}
- decision_maker_role: {{decision_maker_role}}
- is_generic_inbox: {{is_generic_inbox}}
- establishment_name: {{establishment_name}}
- establishment_city: {{establishment_city}}
- establishment_country: {{establishment_country}}
- establishment_category: {{establishment_category}}
- peer_chain_hint: {{peer_chain_hint}}
- target_subject_pattern: {{target_subject_pattern}}

Remember:
- Body 70-100 words, 4-5 sentences, plain text, no exclamation marks, no emoji.
- One URL only: https://wellmap.org (in the CTA sentence).
- Sign-off exactly: "Warm regards,\nJean-Guy de Gabriac\nFounder — World Wellness Weekend".
- If first_name is null, greet "Hi team at <establishment_name>,".
- If city is null, drop the city mention — never write "in null".
- Use only the peer_chain_hint provided — do not name any other chain.
- If target_subject_pattern is provided (A/B/C/D/E), use that pattern; otherwise pick the most natural fit.
```

## 8. Output schema attendu de Haiku

```
JSON Schema strict (à passer dans `output_config.format` de l'API messages.create) :

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "wwwemail",
    "strict": true,
    "schema": {
      "type": "object",
      "additionalProperties": false,
      "required": ["subject", "body"],
      "properties": {
        "subject": {
          "type": "string",
          "minLength": 8,
          "maxLength": 60,
          "description": "Email subject line. Plain text. No emoji. No exclamation marks. No ALL CAPS. No first name. Action-oriented or curiosity-driven. 4-8 words."
        },
        "body": {
          "type": "string",
          "minLength": 350,
          "maxLength": 800,
          "description": "Full email body as plain prose. Greeting line, blank line, 4 sentences (S2-S5), blank line, exact sign-off ('Warm regards,\\nJean-Guy de Gabriac\\nFounder — World Wellness Weekend'). 70-100 words. No markdown, no bullets, no emoji, no exclamation, only one URL: https://wellmap.org."
        }
      }
    }
  }
}
```

Validation Python post-Haiku (fail → 1 retry, sinon fallback hardcodé) :
1. `len(subject) <= 60` et `len(subject) >= 8`
2. `"!" not in subject` et `"!" not in body`
3. `subject != subject.upper()` (anti-ALL-CAPS)
4. `70 <= len(body.split()) <= 110` (petite marge)
5. `body.count("https://wellmap.org") == 1` (exactement 1 URL)
6. `"Jean-Guy de Gabriac" in body` et `"Founder — World Wellness Weekend" in body`
7. Aucun de ces tokens dans subject+body : `{`, `}`, `[`, `]`, `null`, `None`, `undefined`, `{{`, `}}`
8. Si `first_name is None` : aucun prénom courant dans body (regex sur liste de 200 prénoms US/UK/AU les plus communs)
9. Si `role is None` : aucun des mots `Owner|Manager|Director|CEO|GM|Trainer|Coach|Instructor|Founder` dans S1-S4 (autorisé seulement dans la sign-off "Founder —")
10. Si `city is None` : aucune des 300 plus grandes villes US/UK/AU dans body
11. Peer chain whitelist par pays : si country="US" et "David Lloyd" in body → fail ; si country="GB" et ("Equinox" in body or "CorePower" in body) → fail ; si country="AU" et ("David Lloyd" in body or "Equinox" in body or "CorePower" in body) → fail
12. Forbidden words check : `["renowned", "award-winning", "leading", "iconic", "world-class", "personalized", "tailored", "leverage", "synergy", "unlock", "elevate", "unparalleled", "cutting-edge", "game-changer", "I hope this", "I came across", "I was impressed", "Just checking", "Don't miss", "Limited time", "Act now"]` — aucun match dans body.
```

## 9. Plan A/B test

PLAN A/B TEST — 7 SUBJECT VARIANTS x 1 BODY UNIQUE

Phase 1 — Test (280 emails, 40/variant, équilibré US/UK/AU et nominatifs/génériques) :
- Envoi mardi-jeudi semaine 1, 10h-11h heure locale destinataire
- Split aléatoire stratifié : 40 par variant, équilibré sur country (US/UK/AU) et inbox type (nominatif/générique). Génériques routés EXCLUSIVEMENT vers V4/V5/V7 (pas de prénom requis).
- Metric primaire : reply rate (opens faussés par Apple MPP → ignorer)
- Metric secondaire : clic wellmap.org (UTM source=cold, medium=email, campaign=metro_fitness_2026, content=subjV1..V7)
- Metric tertiaire : spam complaint rate (cible <0.10%, kill switch >0.30%)
- Durée test : 5 jours ouvrés pour laisser le temps aux replies naturels

Phase 2 — Scale-up (1168 restants) :
- Choisir le subject variant gagnant (reply rate le plus haut, complaint <0.10%)
- Envoyer en cadence warmup : 80-120/jour/inbox sur 3-5 inboxes secondaires, sur 3 semaines
- Si écart entre top 2 variants < 15% relatif : continuer 50/50 sur les 2 meilleurs

Phase 3 — Follow-up unique J+5 (touch 2) :
- Subject thread (Re:) avec body de 40-60 mots, ton "bumping this up", lien wellmap.org
- Pas de touch 3 (au-delà = fatigue + complaints)

Segmentation supplémentaire :
- Génériques (info@/contact@) : V4, V5, V7 uniquement (jamais V1-V3 qui supposent contexte nominatif)
- Nominatifs : V1, V2, V3, V6 prioritaires
- Hôtels avec piscine+gym : tagger pour sous-test mineur "wellness destination"

Critères d'arrêt :
- Si complaint rate >0.30% sur un variant → kill ce variant
- Si reply rate global <2% à J+10 → revoir le body, pas juste les subjects
- Si délivrabilité Gmail dégrade (bounce >2%) → pause + diagnostic DKIM/SPF/warmup

## 10. Checklist compliance

- [ ] CAN-SPAM (USA) : nom légal Tip Touch International SRL + adresse postale BE complète + lien unsubscribe fonctionnel + sujet non trompeur — tous présents dans footer_compliance_block
- [ ] CCPA/CPRA (Californie) : lien privacy notice disclosant catégories de données + route 'Do Not Sell or Share' — inclus via wellmap.org/privacy
- [ ] UK PECR reg.22 : corporate-subscriber carve-out s'applique aux Ltd/LLP/PLC — FILTRER les sole traders boutique studios UK avant envoi (Companies House lookup ou exclusion manuelle)
- [ ] UK GDPR Art.6(1)(f) légitimate interest : mention explicite dans footer + LIA documentée en interne (pas dans email)
- [ ] UK GDPR Art.14 (données non collectées auprès du sujet) : disclosure data source via lien privacy notice — 1 mois max après obtention, le 1er email satisfait
- [ ] AU Spam Act 2003 inferred consent : email pro publié + rôle public + pitch lié au rôle = OK ; mention explicite 'authorised by Tip Touch' dans footer
- [ ] AU Privacy Act APP 7 : disclosure source des données sur demande (reply email) — phrase ajoutée au footer
- [ ] CANADA CASL : Canada EXCLU à 100% de la liste (vérifier requête SQL preflight : WHERE country IN ('US','GB','AU') uniquement)
- [ ] Opt-out window universel 5 jours ouvrés (le plus strict = AU) — suppression automatique <24h en pratique
- [ ] List-Unsubscribe RFC 8058 header présent avec mailto: ET https:, signé DKIM, endpoint POST one-click sans login/captcha
- [ ] Endpoint unsubscribe sur sous-domaine authentifié DKIM-aligned (unsubscribe.wellmap.org), pas de tracking redirect
- [ ] Pas de scraping LinkedIn, données issues uniquement Apify Google Maps + Apollo (mention dans privacy notice)
- [ ] Tip Touch SRL = contrôleur GDPR : entité, n° BE 0845.876.424, contact DPO mentionnés dans privacy notice liée
- [ ] From, Reply-To, Return-Path tous sur le même domaine secondaire authentifié (alignment DMARC strict)
- [ ] Reply-To pointe vers boîte humaine monitorée (pas no-reply@) — exigence PECR + Spam Act
- [ ] Suppression list pull en temps réel avant chaque batch SendGrid — éviter ré-envoi à opt-outs
- [ ] Génériques info@/contact@ : ton + neutre, pas de prénom inventé — vérifier is_generic_inbox=true côté Python avant appel Haiku

## 11. Checklist deliverability

- [ ] SPF, DKIM, DMARC tous alignés et passants sur domaine secondaire dédié (PAS tip-touch.com principal)
- [ ] DMARC policy minimum p=quarantine (idéalement p=reject), rua/ruf monitoré
- [ ] Domaine secondaire warmé 4-8 semaines AVANT campagne : J1 10-20/jour, +10-15% par jour jusqu'à plateau 80-120/jour/inbox
- [ ] Splitting sur 3-5 inboxes secondaires distinctes : 80-120 envois/jour/inbox étalés sur 3-4 semaines
- [ ] List-Unsubscribe header RFC 8058 : '<https://unsubscribe.wellmap.org/u?t={{token}}>, <mailto:unsubscribe@wellmap.org?subject=unsubscribe&body={{token}}>' + 'List-Unsubscribe-Post: List-Unsubscribe=One-Click'
- [ ] Endpoint POST one-click sans login/captcha/confirmation page (RFC 8058 strict)
- [ ] List-Unsubscribe headers DKIM-signés (vérifier 'show original' sur test Gmail+Yahoo)
- [ ] Subdomain unsubscribe sur authentification DKIM-aligned, pas de clicktracking redirect
- [ ] From: 'Jean-Guy de Gabriac <jean-guy@em.tiptouch.[tld]>' (humain, pas no-reply)
- [ ] Reply-To égal au From, boîte vraiment monitorée, réponse <24h obligatoire pour chaque reply (boost reputation)
- [ ] Envoi mardi-jeudi 10h-11h heure LOCALE destinataire (split timezone US/UK/AU)
- [ ] Plain text strict, pas d'image, pas de logo, pas de tracking pixel, 1 seul lien (https://wellmap.org)
- [ ] Multipart/alternative text+minimal-HTML identiques pour ne pas paraître suspect mais rendu indistinguable d'email perso
- [ ] Subject sans ALL CAPS, sans '!!', sans '???', sans 'FREE!!!' — préférer 'no-cost' ou 'free' isolé
- [ ] Pas plus de 2 follow-ups (3 touches max), follow-up J+5 thread Re:
- [ ] Honorer unsubs <48h max, suppression list pull avant chaque dispatch
- [ ] Spam complaint rate cible <0.10%, kill switch >0.30%
- [ ] TLS opportuniste + MTA-STS configurés sur domaine d'envoi
- [ ] Personnalisation Haiku réelle (city, name, category, peer chain par pays) — pas de '{{}}' qui leak en prod
- [ ] Validation Python post-Haiku : 12 règles anti-hallucination + check absence de placeholders + check len(subject)≤60 + check 'Jean-Guy de Gabriac' présent + check 'https://wellmap.org' présent
- [ ] Tracking : SEULEMENT clics (UTM) et replies — IGNORER opens (Apple MPP fausse 50-60%)
- [ ] Génériques (info@/contact@) routés vers sous-batch séparé avec ton 'Hi team at {{establishment}},' — JAMAIS de prénom inventé
- [ ] Idempotence : check email_sends.contact_id avant chaque appel pour reprise après crash

## 12. Coût estimé

Modèle claude-haiku-4-5 ($1/M input, $5/M output). Par email : ~920 tokens input (system 800 + user 120), ~220 tokens output (subject+body JSON). Brut : ~$0.00199/email × 1448 = $2.88. Avec prompt caching ttl=1h sur system 800 tokens (write 2x au 1er appel, read 0.1x sur les 1447 suivants) : ~$1.82 total. Avec Batches API (-50% sur tout) + caching : ~$0.91 total. Marge retries +30% (validation anti-hallucination échouée → 1 retry) : budget réaliste 1.20$ pour les 1448 emails. Recommandation : utiliser Batches API + caching → coût final attendu < 1$. Coût négligeable vs valeur campagne (potentiel ~50-150 inscriptions wellmap à 2-5% reply→signup).

## 13. Risques et mitigations

RISQUES & MITIGATIONS :

1. HALLUCINATION HAIKU — Risque que Haiku invente un fait sur le club ("award-winning", "since 2010", un nombre de membres). Mitigation : 14 règles d'interdiction explicites dans system prompt + 12 validations Python post-génération (regex anti-marketing words, anti-placeholder leak, peer chain whitelist par pays, prénom whitelist si null). Retry 1x si fail, sinon fallback template hardcodé.

2. PEER CHAIN MISMATCH — Risque que Haiku mentionne David Lloyd à un destinataire US (contradiction crédibilité). Mitigation : peer_chain_hint passé en input et règle stricte "ONLY use the peer_chain_hint provided" + validation Python sur dict de chaînes interdites par pays.

3. PLACEHOLDER LEAK — Risque que "{{city}}" ou "null" arrive en prod si fallback mal géré. Mitigation : validation regex sur `{`, `}`, `[`, `]`, `null`, `None`, `undefined` avant chaque envoi. Logique côté system prompt : "If city is null, drop the segment entirely, never write 'in null'".

4. SOLE TRADERS UK (PECR reg.22) — Risque légal : les boutique studios UK souvent constitués en sole traders nécessitent CONSENT préalable (pas couverts par corporate-subscriber carve-out). Mitigation : filtrer en preflight via Companies House lookup ; OU exclure les noms d'établissement qui ressemblent à sole traders ; OU documenter risque dans LIA et accepter avec opt-out ultra-rapide. Volume UK = 230 → effort raisonnable.

5. CANADA LEAK — Risque qu'un destinataire canadien (CASL) glisse dans la liste US. Mitigation : SQL preflight explicite `WHERE country IN ('US','GB','AU')` + double-check city contre liste de villes canadiennes courantes (Toronto, Vancouver, Montréal...).

6. SPAM COMPLAINT >0.30% — Risque blocage Gmail. Mitigation : kill switch automatique si complaint rate >0.20% (alerte) ou >0.30% (stop campaign). Reply STOP + lien unsubscribe ultra-visible. Suppression list pull avant chaque batch.

7. APPLE MPP FAUX OPENS — Risque d'optimiser sur métrique fausse. Mitigation : tracking primaire = REPLIES uniquement, secondaire = CLICS UTM-trackés, opens ignorés.

8. DELIVRABILITÉ DOMAINE FROID — Risque que le domaine secondaire ne soit pas assez warmé. Mitigation : warmup 4-8 semaines AVANT campagne (Instantly, Mailwarm, ou Warmup Inbox), DKIM/SPF/DMARC vérifiés en p=quarantine min, test envoi sur Gmail+Yahoo+Outlook personnel avant launch.

9. FATIGUE FOLLOW-UP — Risque que le J+5 génère des complaints. Mitigation : 1 SEUL follow-up, thread Re:, body 40-60 mots ultra-court, lien unsubscribe en haut du footer.

10. RATE LIMIT HAIKU EN BURST — Risque ITPM dépassé si on lance 1448 sync en parallèle. Mitigation : Batches API (pas de rate limit RPM, juste cap volume du batch) ; fallback asyncio.Semaphore(5).

11. SUBJECT "FREE" → SPAM — Risque que "free" dans subject déclenche filtres. Mitigation : "free" autorisé MAX 1x dans body (S3 "no fee, no commission"), JAMAIS dans subject sauf en variant V1 où c'est isolé sans "!!!" ni ALL CAPS (Sparkle 2026 : contexte > mot isolé). Comparer V1 vs V2/V5 en A/B et killer V1 si complaint rate plus haut.

12. JEAN-GUY ABSENCE — Risque que la signature ne sorte pas exactement "Jean-Guy de Gabriac, Founder — World Wellness Weekend". Mitigation : validation Python `"Jean-Guy de Gabriac" in body and "Founder — World Wellness Weekend" in body` ; retry si absent.

13. RÉPONSE NON GÉRÉE — Risque de ghoster les répondants (pire que ne pas envoyer). Mitigation : boîte reply-to monitorée par humain, SLA réponse <24h, template de réponse prêt (envoi du PDF "Your CLUB or STUDIO should participate" sur demande, lien wellmap.org/sign-up).

14. SUBJECT V1 CONTIENT "free" — risque variant-specific spam. Mitigation : A/B le mesure ; si V1 sous-performe ou complaint plus haut, garder V2/V3/V5 comme winners.

15. CATEGORY ENUM MAL MAPPÉE — Risque qu'un établissement réel ait une category Supabase ("yoga studio", "pilates") qui ne mappe pas exactement à l'enum. Mitigation : preflight Python normalise via dict fuzzy ("yoga studio" → yoga_pilates, "pilates studio" → yoga_pilates, "reformer" → reformer_pilates, "fitness center" → gym, "boutique gym" → boutique_fitness, "hotel spa" → hotel_wellness, fallback → other_fitness). Log les unmapped.