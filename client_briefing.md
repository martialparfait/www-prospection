# World Wellness Weekend — Stratégie de prospection mondiale

**Document de cadrage et plan de campagne**

---

## Sommaire

1. [Synthèse exécutive](#1-synthèse-exécutive)
2. [Objectif et périmètre](#2-objectif-et-périmètre)
3. [Travaux réalisés à ce jour](#3-travaux-réalisés-à-ce-jour)
4. [Stratégie retenue](#4-stratégie-retenue)
5. [Cadre juridique et conformité](#5-cadre-juridique-et-conformité)
6. [Architecture technique et outils](#6-architecture-technique-et-outils)
7. [Plan d'exécution par phases](#7-plan-dexécution-par-phases)
8. [Budget prévisionnel](#8-budget-prévisionnel)
9. [Résultats attendus et indicateurs de succès](#9-résultats-attendus-et-indicateurs-de-succès)
10. [Risques identifiés et mesures de mitigation](#10-risques-identifiés-et-mesures-de-mitigation)
11. [Décisions attendues du client](#11-décisions-attendues-du-client)
12. [Annexes](#12-annexes)

---

## 1. Synthèse exécutive

### Le projet en une phrase

Identifier de manière conforme et industrialisée les responsables (gérant, manager, directeur général) de **clubs de fitness, studios de yoga et Pilates, hôtels avec installations sport/spa, dojos d'arts martiaux et running clubs** dans **7 pays cibles**, et les inviter à participer gratuitement au **World Wellness Weekend**.

### Les 5 décisions structurantes

1. **Approche par phases**, pas en big bang. Validation d'un pilote (POC) sur **2 000 établissements aux USA** avant industrialisation. Cela limite le risque budgétaire et permet d'ajuster le pipeline avant d'investir à pleine échelle.
2. **Stack hybride open-data + outils SaaS spécialisés**, pas de développement custom complexe. Choix qui privilégie le time-to-market et le coût maîtrisé sur la sophistication technique.
3. **Conformité juridique première priorité** : politique de confidentialité publiée AVANT le 1er email, analyse d'intérêt légitime documentée, lien d'opt-out un clic, exclusion du Canada de la phase cold email (régime CASL incompatible).
4. **Identification du gérant via croisement de sources publiques** (site web officiel + données ouvertes Google Maps/OpenStreetMap + bases B2B conformes RGPD), sans scraping LinkedIn (risque juridique et opérationnel rédhibitoire en 2026).
5. **Budget pilote forfaitaire de 1 400 €** (outils, validation juridique et prestation inclus) pour mesurer les indicateurs réels avant tout engagement à grande échelle. Décision d'industrialisation conditionnée aux résultats du pilote.

### Promesse de résultat — pilote USA

À partir de **2 000 établissements** scrapés et enrichis, sous hypothèses validées par 3 études de marché récentes :

- **Entre 800 et 1 200 emails de gérants nominatifs vérifiés** (taux de match 40–60 %)
- **Coût total pilote : 1 400 €** forfaitaires (outils, validation juridique et prestation inclus — voir détail §8.1)
- **Délai : 3 semaines** depuis le feu vert
- **Conversion estimée à l'inscription** : entre **8 % et 15 %** sur les emails délivrés, soit **~80 à 180 établissements inscrits** au World Wellness Weekend dès la première vague pilote


---

## 2. Objectif et périmètre

### Objectif final

Recruter en masse, à l'échelle mondiale, des établissements de bien-être pour qu'ils s'inscrivent gratuitement comme participants au World Wellness Weekend (initiative annuelle non-lucrative en faveur de la santé et du bien-être, organisée par Tip Touch International).

### Verticaux ciblés

Les 6 catégories d'établissements visées en priorité :

| Vertical | Profil type | Décideur typique |
|---|---|---|
| **Clubs de fitness** | Salles de sport, CrossFit, Functional training | Owner / Manager |
| **Studios de yoga** | Studios indépendants, écoles certifiées | Owner |
| **Studios de Pilates** | Boutique studios, instituts spécialisés | Owner / Studio Manager |
| **Hôtels avec piscine ET salle de sport** | 3-5 étoiles, indépendants ou chaînes | General Manager (GM) |
| **Dojos d'arts martiaux** | Karaté, judo, jiu-jitsu, taekwondo, MMA | Sensei / Owner |
| **Running clubs** | Clubs locaux et associatifs | Coordinateur / Président |

### Pays cibles

7 pays demandés par le client :

🇺🇸 **USA** • 🇨🇦 **Canada** • 🇬🇧 **Royaume-Uni** • 🇦🇺 **Australie** • 🇳🇿 **Nouvelle-Zélande** • 🇫🇷 **France** • 🇪🇸 **Espagne**

### Volume d'objectif

- **Pilote (mois 1)** : 2 000 établissements traités
- **Phase 1.5 (mois 2)** : 30 000–50 000 établissements (extension verticaux + UK/AU/NZ)
- **Phase 2 (mois 3+)** : 100 000–200 000 établissements (ajout FR/ES, montée en charge)

### Hors-périmètre de cette phase

- 🇨🇦 Canada en cold email — exclu pour des raisons juridiques (loi CASL, voir section 5)
- Scraping LinkedIn — exclu pour des raisons juridiques et de risque opérationnel
- Téléphone (cold calling) — non demandé, non couvert par cette stratégie
- Création du site d'inscription — déjà existant côté client (https://map.world-wellness-weekend.org/)

---

## 3. Travaux réalisés à ce jour

### 3.1. Recherche stratégique

**Trois rapports de recherche approfondie** ont été produits et croisés sur les sujets suivants :
- Architecture technique d'une plateforme de prospection B2B mondiale
- Sources de données mondiales (APIs, datasets ouverts, scraping)
- Identification des dirigeants à grande échelle
- Conformité RGPD/CASL/CAN-SPAM par juridiction
- Tarifs et benchmarks 2026 des fournisseurs spécialisés

**Conclusions clés convergentes** :
- Aucune source unique ne couvre les 7 pays sur les 6 verticaux ; une **architecture hybride open-data + scraping ciblé + enrichissement en cascade** est nécessaire.
- L'identification du dirigeant nominatif plafonne à **40-65 % de match-rate**, c'est le poste le plus difficile et le plus coûteux.
- Le scraping LinkedIn est devenu **rédhibitoire en 2026** (fermeture forcée de Proxycurl en juillet 2025, sanction CNIL de 240 000 € contre Kaspr en décembre 2024).
- Le risque numéro 1 du projet n'est pas technique mais **juridique** (RGPD côté EU, CASL côté Canada).

### 3.2. Infrastructure projet

Un dossier de travail dédié a été créé et structuré pour héberger l'ensemble des livrables :

```
WWW Prospection/
├── .gitignore                      Protection des secrets
├── .secrets/                       Credentials Service Account Google (chmod 700)
├── README.md                       Documentation interne
├── setup_sheet.py                  Script Python de gestion du Sheet
├── privacy_policy_fr.md            Politique de confidentialité (FR)
├── privacy_policy_en.md            Politique de confidentialité (EN)
└── client_briefing.md              Le présent document
```

### 3.3. Référentiel de données — Google Sheet

Un Google Sheet maître a été créé et structuré avec 4 onglets opérationnels :

| Onglet | Contenu | Usage |
|---|---|---|
| **Catégories** | 26 typologies d'établissements de bien-être | Taxonomie partagée, référentiel filtrable |
| **Pays** | 199 pays (norme ISO 3166-1) avec capitales et continents | Référentiel pour filtrage et reporting |
| **Régions** | 218 villes principales (Belgique, France, Espagne, Allemagne) | Géographie de référence pour l'EU |
| **Établissements** | Structure prête (12 colonnes), à alimenter | Table de travail pour le pilote et la suite |

**Lien d'accès** : https://docs.google.com/spreadsheets/d/15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0

À noter : ce Sheet sert de référentiel de pilotage humain. **À partir de ~50 000 établissements**, la donnée principale migrera vers une base PostgreSQL (Supabase) plus adaptée à la masse, le Sheet restant pour la taxonomie et l'export de listes de travail.

### 3.4. Conformité RGPD — premier socle

**Politique de confidentialité bilingue (FR + EN) rédigée**, conforme au RGPD et aux régimes équivalents des 7 pays cibles. Couvre :
- Identification du responsable de traitement (Tip Touch International)
- Catégories de données collectées (visiteurs site + prospects)
- Sources des données (article 14 RGPD — transparence)
- Bases légales (intérêt légitime + consentement + obligation légale)
- Durées de conservation (3 ans après dernier contact actif)
- Droits des personnes (accès, rectification, effacement, opposition, portabilité)
- Procédure d'exercice des droits (lien opt-out un clic, réponse <48h)
- Politique de cookies
- Sécurité et notification de violation de données (72h)

**À compléter avant publication** : adresse postale de la SRL, email privacy dédié, hébergeur du site, outils analytiques utilisés. *4 champs marqués clairement dans les deux fichiers.*


---

## 4. Stratégie retenue

### 4.1. Principe directeur — phasage

L'enseignement central des trois rapports de recherche : **personne ne réussit ce type de projet en mode "tout d'un coup"**. La stratégie retenue est un déploiement en **3 phases progressives** avec mesure des résultats à chaque palier.

```
PHASE PILOTE (Mois 1)
└── 2 000 fiches • USA seul • 3 verticaux (yoga/pilates/fitness)
    │
    ├── Mesure du taux de match gérant nominatif
    ├── Mesure du coût réel par lead vérifié
    └── Mesure du taux de réponse à la 1ʳᵉ campagne email
        │
        └── Décision Go/No-Go pour Phase 1.5

PHASE 1.5 (Mois 2)
└── 30-50k fiches • USA + UK + AU + NZ • 6 verticaux
    │
    └── Validation avant Phase 2

PHASE 2 (Mois 3+)
└── 100k+ fiches • Ajout France + Espagne (avec validation juridique préalable)
    └── Canada réservé à l'outreach manuel hors cold email
```

### 4.2. Pourquoi ce phasage et ces choix géographiques

| Choix | Raison |
|---|---|
| **USA en pilote** | Marché le plus grand (~150-200k établissements ciblables), régime CAN-SPAM le plus simple (opt-out), culture web "About Us" qui facilite l'identification du gérant. |
| **UK + AU + NZ en phase 1.5** | Anglais (réutilisation du template email), régimes juridiques proches du pilote, volume substantiel, pas de barrière linguistique pour le client. |
| **France + Espagne en phase 2** | RGPD strict, nécessite un LIA validé juridiquement et une politique de confidentialité publiée. Vaut mieux l'aborder en seconde intention avec le pilote validé. |
| **Canada exclu en cold email** | Loi CASL = opt-in obligatoire pour entité commerciale (la SRL n'est pas une "registered charity" malgré le caractère non-lucratif de l'événement). Risque jusqu'à 10M$ CAD/violation. À traiter via outreach manuel ou inscription via site. |

### 4.3. Pourquoi 3 verticaux en pilote, pas 6

Les 3 verticaux choisis (**yoga, Pilates, fitness**) ont :
- Des sources de données identiques (Google Maps + OpenStreetMap)
- Des profils de décideurs similaires (owner-operator, manager local)
- Une présence web homogène (sites publics avec pages "Team")

Les 3 autres (**martial arts, running clubs, hôtels avec piscine+gym**) sont plus complexes à traiter :
- Les hôtels exigent un filtrage par équipements (`pool` AND `gym`) qui demande un scraping plus profond
- Les running clubs sont souvent associatifs et moins présents sur Google Maps
- Les dojos sont fragmentés entre fédérations nationales

Les ajouter en pilote diviserait l'effort et compliquerait la mesure. **On valide d'abord le pipeline simple, on étend ensuite.**

### 4.4. Pourquoi pas de scraping LinkedIn

Décision explicite, basée sur trois faits récents :

- **Janvier 2025** : LinkedIn dépose plainte contre Proxycurl (leader du marché des APIs LinkedIn-data), qui ferme définitivement en juillet 2025.
- **Décembre 2024** : la CNIL inflige une amende de **240 000 €** à Kaspr pour scraping LinkedIn de 160 millions de contacts.
- **Mars 2025** : LinkedIn supprime les Company Pages d'Apollo.io et Seamless.AI.

Bâtir une stratégie de prospection sur LinkedIn = bombe à retardement juridique et opérationnelle. **Toutes les sources crédibles convergent sur cette exclusion** en 2026.

### 4.5. Pourquoi un mix open-data + SaaS, pas de gros build custom

Trois raisons :

1. **Time-to-market** : un développement custom complet d'orchestration agentique (LangGraph + Postgres + Crawlee + LLM batch) prendrait 6-8 semaines. Le client veut envoyer ses premiers emails ce mois-ci.
2. **Économie au démarrage** : l'analyse comparée build vs buy montre qu'un développement custom n'est rentable qu'à partir de **50-100k contacts enrichis par mois récurrents**. Au pilote (2 000 fiches), le buy/SaaS coûte **5 à 10 fois moins cher** en cash et en temps.
3. **Réversibilité** : architecture en cascade découplée, chaque outil peut être remplacé indépendamment. Si Apollo change de pricing, on bascule sur un concurrent en 48 heures.

---

## 5. Cadre juridique et conformité

### 5.1. Position de Tip Touch International

Tip Touch International SRL est une **société commerciale belge** (numéro d'entreprise BE 0845.876.424). Bien que l'événement World Wellness Weekend soit non-lucratif et d'intérêt général (santé et bien-être), l'**émetteur juridique** des emails reste une entité commerciale. Cela a deux conséquences :

1. **Les exemptions "registered charity"** des lois anti-spam canadienne (CASL), australienne (Spam Act) et néo-zélandaise (UEMA) **ne s'appliquent pas**. Le régime commercial standard de chaque pays s'applique.
2. **Le caractère non-lucratif et d'intérêt général** de l'opération **renforce considérablement la base "intérêt légitime" du RGPD** dans l'EU/UK : le test de mise en balance des intérêts (LIA) passe avec une forte marge.

### 5.2. Régime applicable par pays

| Pays | Régime | Contraintes principales | Statut phase pilote/scale |
|---|---|---|---|
| 🇺🇸 USA | **CAN-SPAM Act** | Opt-out + adresse postale physique + désinscription <10 jours ouvrables | ✅ Phase pilote |
| 🇬🇧 UK | **PECR + UK GDPR** | Intérêt légitime documenté pour les emails nominatifs | ✅ Phase 1.5 |
| 🇦🇺 Australie | **Spam Act 2003** | "Inferred consent" admis pour B2B avec lien fonctionnel clair | ⚠️ Phase 1.5 (à valider juridiquement) |
| 🇳🇿 Nouvelle-Zélande | **UEMA** | Similaire à l'Australie | ⚠️ Phase 1.5 (à valider juridiquement) |
| 🇫🇷 France | **RGPD + LCEN** | LIA + Article 14 + opt-out un clic | ✅ Phase 2 |
| 🇪🇸 Espagne | **RGPD + LSSI** | Plus strict que la France, vérifications additionnelles | ⚠️ Phase 2 |
| 🇨🇦 Canada | **CASL** | **Opt-in obligatoire** pour entité commerciale | ❌ Exclu du cold email — outreach manuel ou inscription via site |

### 5.3. Mesures de conformité mises en œuvre

**Avant tout 1er envoi**, les éléments suivants seront opérationnels :

1. ✅ **Politique de confidentialité bilingue** publiée sur le site (rédigée — voir section 3.4)
2. 🔄 **Document LIA (Legitimate Interest Assessment)** d'1 à 2 pages — *en cours, livraison sous 48h*
3. 🔄 **Lien d'opt-out un clic** dans chaque email + header `List-Unsubscribe` (RFC 8058)
4. 🔄 **Adresse postale physique de Tip Touch** dans la signature (exigence CAN-SPAM)
5. 🔄 **Mention transparente de la source des données** dans le 1er email (exigence article 14 RGPD)
6. 🔄 **Registre des opt-out centralisé** : tout désinscrit n'est plus jamais re-contacté, traitement <48h
7. 🔄 **Authentification email complète** : SPF + DKIM + DMARC sur le domaine d'envoi (exigence Gmail/Yahoo/Microsoft 2024-2025)

### 5.4. Exposition au risque

| Risque juridique | Probabilité | Impact maximal | Mitigation |
|---|---|---|---|
| Plainte APD/CNIL d'un destinataire | Faible | 4% du CA mondial (jusqu'à 20M€) | Politique + LIA + opt-out + transparence article 14 |
| Suspension de SendGrid pour cold outreach | Moyenne | Interruption campagne | Plan B Smartlead/Instantly (2 jours pour basculer) |
| Surcharge plaintes spam Gmail | Moyenne | Perte délivrabilité domaine | Volume progressif + vérification NeverBounce + monitoring Postmaster Tools |
| Erreur de ciblage Canada | Faible (si filtre IP/pays appliqué) | Action CRTC, jusqu'à 10M$ CAD | Filtre strict par pays dans la base |

### 5.5. Validation juridique recommandée

**Avant le 1er envoi**, une revue par un **avocat IT/RGPD belge** est recommandée :
- Durée : 1 heure de consultation
- Coût indicatif : 150-300 €
- Périmètre : politique de confidentialité, LIA, template du 1er email, registre Article 30

Cette validation est un investissement marginal qui sécurise l'ensemble de la stratégie sur 12-24 mois et constitue une preuve de bonne foi en cas de contrôle.

---

## 6. Architecture technique et outils

### 6.1. Vue d'ensemble du pipeline

```
[ Sources publiques ]
  ├── OpenStreetMap (gratuit, ODbL)
  ├── Overture Maps Foundation (gratuit, CDLA)
  └── Google Maps / Apify (~$3 / 1 000 fiches)
                │
                ▼
[ Base de travail ]
  └── Google Sheet "Établissements" (pilote ≤ 2 000 lignes)
       Migration future vers PostgreSQL/Supabase
                │
                ▼
[ Crawl et extraction ]
  ├── Playwright (open source, navigateur automatisé)
  └── Claude Haiku 4.5 (~$0,01 / fiche, extraction owner depuis sites web)
                │
                ▼
[ Cascade d'enrichissement ]
  ├── Apollo.io (recherche email + LinkedIn d'un nom + domaine)
  ├── Dropcontact (résolution algorithmique RGPD-friendly)
  └── Hunter.io (pattern-based, fallback)
                │
                ▼
[ Vérification ]
  └── NeverBounce (~$0,008 / email) — bounce rate <2 % avant envoi
                │
                ▼
[ Envoi ]
  └── SendGrid via domaine secondaire pré-warmupé du client
                │
                ▼
[ Suivi et opt-out ]
  ├── Tracking ouvertures/clics/réponses dans SendGrid
  └── Registre opt-out centralisé (table dédiée)
```

### 6.2. Justification des outils choisis

| Outil | Pourquoi celui-là (et pas un autre) | Coût |
|---|---|---|
| **Apify Google Maps Scraper** | 4-10× moins cher que Google Places API officielle. 27 000+ Actors prêts à l'emploi, intégration directe par API. Alternative légalement plus sûre que SerpApi (procédure Google v. SerpApi en cours, audience mai 2026). | ~$3 / 1 000 fiches |
| **Claude Haiku 4.5 (Anthropic)** | Modèle LLM le mieux structuré pour extraction JSON depuis HTML. Pricing très bas avec Batch API + prompt caching. Familier à l'équipe de développement. | ~$0,01 / fiche |
| **Apollo.io** | Plus grande base B2B (275M contacts) avec API solide et tier gratuit pour démarrer. Bon ratio qualité/prix sur SMB (notre cible majoritaire). | $49-79 / mois |
| **Dropcontact** | **Seul outil d'enrichissement RGPD-by-design** audité par la CNIL. Génération algorithmique sans stockage de PII. Indispensable pour les volets France et Belgique. | À partir de 24 €/mois |
| **NeverBounce** | Standard du marché pour la vérification email avant envoi. Réduit le bounce rate à <2 %, condition de survie de la délivrabilité. | ~$0,008 / email |
| **SendGrid** (existant client) | Compte existant + domaine secondaire pré-warmupé. Permet de démarrer immédiatement sans coût additionnel d'infrastructure email. ⚠️ Plan B identifié (Smartlead/Instantly) si l'AUP devient un blocage. | Inclus existant |
| **Google Sheets + Service Account** | Simplicité maximale au pilote. Visibilité directe pour le client. À ce volume (2 000 lignes), aucune raison d'introduire une base relationnelle plus lourde. | Gratuit |

### 6.3. Outils volontairement écartés

| Outil écarté | Pourquoi |
|---|---|
| **Google Places API officielle** | Trop coûteuse au volume cible (8 000-15 000 €/mois économisés en passant par Apify). ToS restrictifs sur le stockage long terme. |
| **Cognism** (premium B2B) | 15 000–25 000 €/an de minimum contractuel. Surdimensionné pour le pilote. À reconsidérer en phase 2 si volume EU >100k/mois. |
| **ZoomInfo** (premium B2B US) | Trop US-centric pour la stratégie mondiale, et trop coûteux (15-50k$/an) pour la cible TPE/SMB visée. |
| **Clay** (orchestrateur enrichissement) | $185-720/mois — efficace pour structurer la cascade d'enrichissement, mais trop cher au pilote. À reconsidérer dès que le volume mensuel dépasse 10k fiches. |
| **PhantomBuster / Evaboot** (LinkedIn) | Risque juridique LinkedIn écarté par décision stratégique (voir section 4.4). |
| **Bright Data** (proxies premium) | Surdimensionné — les sites cibles (yoga studios, fitness clubs) sont peu protégés et ne nécessitent pas de proxies résidentiels au prix élevé. |

---

## 7. Plan d'exécution par phases

### 7.1. Phase pilote — 3 semaines (mois 1)

**Objectif** : valider le pipeline complet sur un échantillon mesurable avant tout investissement à grande échelle.

#### Semaine 1 — Conformité et collecte

| Jour | Action | Responsable | Livrable |
|---|---|---|---|
| J1-J2 | Validation juridique de la politique de confidentialité + LIA | Avocat IT (1h) | Document validé |
| J1-J2 | Publication politique sur https://world-wellness-weekend.org | Client | Page live |
| J1-J3 | Configuration SendGrid + SPF/DKIM/DMARC sur domaine d'envoi | Développeur | Configuration validée par test |
| J3-J5 | Scraping Apify Google Maps : USA × 3 verticaux × ~10 grandes villes | Développeur | ~3 000-4 000 fiches brutes |
| J5-J7 | Filtrage, dédoublonnage, normalisation | Développeur | 2 000 fiches qualifiées dans le Sheet |

#### Semaine 2 — Enrichissement

| Jour | Action | Livrable |
|---|---|---|
| J8-J10 | Crawl des sites web (Playwright + Claude Haiku) | Owner identifié sur ~50 % des fiches |
| J10-J12 | Cascade Apollo → Dropcontact → Hunter | Email candidat sur 70-80 % des fiches |
| J12-J14 | Vérification NeverBounce | 800-1 200 emails confirmés deliverable |

#### Semaine 3 — Première campagne

| Jour | Action | Livrable |
|---|---|---|
| J15-J17 | Rédaction et A/B test du 1er email (en anglais, conforme CAN-SPAM) | 2 variantes prêtes |
| J17-J18 | Test seed (10 emails internes) + monitoring délivrabilité | Validation infrastructure |
| J18-J21 | Envoi progressif 100/jour → 300/jour | 1 000+ emails envoyés |
| J21+ | Mesure des indicateurs (open, click, reply, opt-out, inscriptions) | Rapport pilote |

### 7.2. Phase 1.5 — Extension verticaux et géographie (mois 2)

**Conditions d'entrée** : pilote validé sur les KPIs (voir section 9).

- Ajout des 3 verticaux complémentaires (martial arts, running clubs, hôtels piscine+gym)
- Extension à UK + Australie + Nouvelle-Zélande
- Volume cible : **30 000-50 000 fiches** scrapées, **15 000-25 000 emails** vérifiés
- Optionnel : passage à Smartlead/Instantly si SendGrid montre des limites

### 7.3. Phase 2 — Échelle et marchés EU (mois 3+)

- Validation juridique RGPD pour France et Espagne (avocat IT, 1-2h additionnelles)
- Extension France + Espagne avec templates d'email localisés
- Volume cible : **100 000-200 000 fiches** au total
- Migration Google Sheet → PostgreSQL/Supabase pour la donnée principale
- Mise en place reporting automatisé (Looker Studio ou équivalent)

---

## 8. Budget prévisionnel

L'engagement initial se décompose en deux étapes : la **phase pilote** (forfaitaire, validation du périmètre) et la **finalisation** (consolidation, relances, documentation pour passage en production).

Tarif horaire de prestation : **50 €/h** (taux net hors taxes, freelance).

### 8.1. Phase pilote — 1 400 € forfaitaires (mois 1, 3 semaines)

Forfait tout inclus pour la mise en place et l'exécution complète du pilote sur 2 000 établissements aux USA (yoga + Pilates + fitness).

| Poste | Détail | Coût |
|---|---|---|
| **Outils & abonnements SaaS** | Apify (~15 €), Claude API (~10 €), Apollo Basic (49 €), Dropcontact 500 crédits (24 €), Hunter Starter (34 €), NeverBounce (~16 €), domaine secondaire (~12 €), Google Workspace 2 inboxes (~12 €), réserve consommation (~25 €) | **~200 €** |
| **Validation juridique** | Avocat IT/RGPD belge — 1 h de consultation pour valider politique de confidentialité, LIA et template du 1er email | **~200 €** |
| **Travail de prestation** (architecture, scraping, enrichissement, rédaction email, première campagne, monitoring, livrables) | ~20 h × 50 €/h | **1 000 €** |
| **TOTAL PILOTE FORFAITAIRE** | | **1 400 €** |

**Ce que couvre le forfait pilote** :
- Configuration complète du pipeline (scraping, enrichissement, vérification, envoi)
- Scraping et qualification de 2 000 établissements
- Enrichissement et obtention de 800-1 200 emails de gérants vérifiés
- Rédaction et A/B test du 1er email
- Première vague de campagne (1 000+ emails délivrés)
- Rapport de mesure complet (KPIs réels mesurés vs cibles)
- Recommandation Go/No-Go pour la finalisation

### 8.2. Finalisation et clôture — ~2 000 € (semaines 4-6)

Consolidation du pilote, exploitation des premiers retours, et préparation pour passage en production. **Ne couvre pas l'extension à pleine échelle** (6 verticaux × 6 pays), qui fera l'objet d'un devis séparé une fois les KPIs validés (voir §8.4).

| Poste | Détail | Coût |
|---|---|---|
| **Outils & consommation prolongée** | Reconduction des abonnements mensuels (Apollo, Dropcontact, Hunter, Google Workspace) + consommation Apify/NeverBounce sur les vagues additionnelles | **~400 €** |
| **Travail de prestation** | ~32 h × 50 €/h — bilan KPIs détaillé, optimisation des templates et du timing, 1-2 vagues de relances, vague d'extension limitée si KPIs validés, documentation technique pour handover | **1 600 €** |
| **TOTAL FINALISATION** | | **~2 000 €** |

**Ce que couvre la finalisation** :
- Rapport KPIs détaillé du pilote complet (open, click, reply, opt-out, inscriptions)
- Optimisation des templates et du timing d'envoi à partir des retours réels
- 1 à 2 vagues de relances sur les non-répondants
- Vague d'extension limitée (500-1 000 fiches additionnelles) si les KPIs valident le pipeline
- Documentation technique du pipeline (procédures, scripts commentés) pour handover ou continuation
- Recommandations chiffrées pour la suite (extensions verticales, géographiques)

### 8.3. Synthèse — engagement initial

| Étape | Investissement | Durée | Périmètre |
|---|---|---|---|
| **Pilote** | 1 400 € forfaitaire | Mois 1 (3 sem.) | 2 000 fiches USA × 3 verticaux, 1ʳᵉ vague |
| **Finalisation** | ~2 000 € | Semaines 4-6 | Bilan, relances, optimisations, documentation |
| **TOTAL ENGAGEMENT INITIAL** | **~3 400 €** | ~6 semaines | Pilote complet, prêt pour passage en production |

### 8.4. Phases ultérieures de scaling (hors engagement initial)

Si le pilote valide les KPIs (voir §9), l'extension à pleine échelle (6 verticaux × 6 pays cibles hors Canada cold email) fera l'objet d'un **devis séparé**, à confirmer sur la base des résultats réels du pilote. Estimations indicatives à titre d'aide à la décision :

| Extension | Périmètre indicatif | Estimation |
|---|---|---|
| **Phase 1.5** — Ajout des 3 verticaux complémentaires (martial arts, running clubs, hôtels piscine+gym) + extension UK/AU/NZ | ~30-50k établissements traités | ~3 000-4 000 € |
| **Phase 2** — Ajout France et Espagne + validation juridique additionnelle + migration vers infrastructure Postgres | ~100-200k établissements traités au cumulé | ~8 000-12 000 € |
| **Régime de croisière** | Maintien du volume + monitoring | ~3 000-4 500 € / mois récurrents |

Ces estimations seront affinées et confirmées au moment de la décision d'extension. Le client peut également décider de piloter lui-même les phases ultérieures avec un appui ponctuel à la demande (50 €/h).

### 8.5. Pourquoi ce budget est raisonnable

Trois éléments de référence :

- **Comparaison full-SaaS** : une approche "clé en main" type Clay Pro + Apollo Org + Cognism + Instantly + Google Workspace × 15 démarre à **3 500-4 500 € / mois** dès le 1er mois, soit **plus que l'engagement initial complet** proposé ici. La différence : ce projet inclut la **conception du pipeline et l'expertise conformité**, pas un simple abonnement.
- **Coût par contact enrichi** : sur le pilote (1 400 € pour ~1 000 emails vérifiés), cela revient à **~1,40 € par lead vérifié de gérant nominatif**. À l'échelle des phases ultérieures, ce coût descend mécaniquement vers 0,30-0,50 € par lead.
- **Coût d'opportunité de la conformité** : la sanction CNIL Solocal de mai 2025 a coûté **900 000 €** à un acteur ayant négligé les mêmes étapes de conformité que ce budget intègre. La validation juridique (~200 €) est une assurance, pas une dépense.

---

## 9. Résultats attendus et indicateurs de succès

### 9.1. KPIs mesurables — pilote (2 000 fiches USA)

Les 5 indicateurs qui seront mesurés et reportés à la fin de la phase pilote :

| KPI | Cible | Seuil minimal acceptable |
|---|---|---|
| **Taux de match dirigeant nominatif** | 50 % (1 000 sur 2 000) | 35 % (700) |
| **Taux de vérification email valide** | 80 % | 70 % |
| **Coût par lead vérifié** | < 0,30 € | < 0,40 € |
| **Bounce rate à l'envoi** | < 2 % | < 3 % (au-delà : pause) |
| **Reply rate à la 1ʳᵉ campagne** | 8-15 % | > 4 % |

### 9.2. Conversion attendue — pilote

À partir de 2 000 fiches initiales :

```
2 000 fiches scrapées
    │
    ├── Filtrage (sites web actifs, non doublons)  →  ~1 700 fiches qualifiées
    │
    ├── Cascade enrichissement (40-60 % match)     →  800-1 200 emails de gérants
    │
    ├── Vérification NeverBounce (75-85 % valides) →  600-1 000 emails valides
    │
    ├── Délivrabilité réelle (95-98 %)             →  570-980 emails délivrés
    │
    ├── Taux de réponse (8-15 %)                   →  45-150 réponses
    │
    └── Conversion en inscription événement         →  ~80-180 établissements
        (estimé : 50-80 % des répondants)              inscrits au WWW
```

### 9.3. Projection à 6 mois

Si le pilote valide les hypothèses :

| Mois | Fiches scrapées (cumul) | Emails délivrés (cumul) | Inscriptions WWW (cumul) |
|---|---|---|---|
| Mois 1 (pilote) | 2 000 | ~1 000 | ~100-180 |
| Mois 2 (1.5) | 50 000 | ~25 000 | ~2 000-4 000 |
| Mois 3 (2 — phase EU) | 150 000 | ~70 000 | ~5 000-10 000 |
| Mois 4-6 (régime de croisière) | 400 000+ | ~150 000+ | ~10 000-20 000+ |

**Note importante sur les projections** : ces estimations s'appuient sur des benchmarks publics 2025-2026 pour des opérations cause-marketing similaires. **Le taux de réponse réel dépend fortement de la qualité du message et du timing par rapport à l'événement**. La phase pilote sert précisément à calibrer ces hypothèses sur le cas spécifique du World Wellness Weekend.

### 9.4. Ce qui constitue un échec

Pour la transparence client, voici les seuils à partir desquels le projet doit être réévalué :

- Match-rate dirigeant **< 25 %** sur le pilote → revoir la stack d'enrichissement
- Reply rate **< 1 %** sur la 1ʳᵉ campagne → réécrire intégralement le message
- Bounce rate **> 5 %** → pause immédiate, audit de la chaîne de vérification
- Plus de **3 plaintes spam pour 1 000 envois** → revoir le ciblage et le contenu

---

## 10. Risques identifiés et mesures de mitigation

| # | Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **Match-rate gérant inférieur aux attentes** (sites web sans page Team, Google sans nom de manager) | Moyenne | Moyen | Cascade multi-sources Apollo + Dropcontact + Hunter ; possibilité d'envoi à `info@` génériques en fallback |
| 2 | **SendGrid ferme le compte pour cold outreach** | Moyenne | Élevé | Plan B Smartlead/Instantly identifié, bascule en 48h |
| 3 | **Domaine d'envoi cramé en délivrabilité** | Faible (déjà warmupé) | Élevé | Volume progressif + monitoring Postmaster Tools + warmup continu en arrière-plan |
| 4 | **Plainte RGPD d'un destinataire EU** | Faible | Élevé | Politique + LIA + opt-out un clic + traitement <48h + validation juridique préalable |
| 5 | **Coûts API Apify/Claude qui dérapent** | Faible | Moyen | Budget alerts configurés à 80 % du seuil, kill-switch automatique |
| 6 | **Évolutions juridiques 2026 défavorables** (DUAA UK, ePrivacy EU, audience Google v. SerpApi en mai) | Moyenne | Variable | Veille mensuelle, architecture découplée pour basculer fournisseurs |
| 7 | **Faux positifs dédoublonnage** (mêmes établissements en doublon dans plusieurs sources) | Élevée | Faible | Fuzzy matching sur (nom normalisé, ville, téléphone, domaine) ; revue manuelle des clusters >50 |
| 8 | **Réponses négatives massives ("c'est du spam")** | Faible (cause-marketing favorable) | Moyen | Test seed avant envoi en masse, A/B sur l'objet, monitoring du sentiment |

---

## 11. Décisions attendues du client

Pour démarrer la phase pilote dans les meilleures conditions, **5 validations** sont attendues de Tip Touch International :

### 11.1. Validation stratégique

✅ **Décision n°1** : approbation du périmètre pilote (USA × 3 verticaux × 2 000 fiches × 3 semaines × forfait 1 400 €)

✅ **Décision n°2** : approbation de l'exclusion du Canada du cold email (outreach manuel ou inscription via site uniquement)

### 11.2. Données nécessaires pour finaliser la conformité

✅ **Décision n°3** : confirmation des champs `[À COMPLÉTER]` dans la politique de confidentialité :
- Adresse postale officielle de Tip Touch International (récupérable BCE)
- Email privacy dédié (suggestion : `privacy@world-wellness-weekend.org`)
- Hébergeur du site (Vercel ? OVH ? Autre ?)
- Outils analytiques utilisés sur le site

✅ **Décision n°4** : feu vert pour la consultation juridique (avocat IT belge, 1h, 150-300 €). Cette validation conditionne l'envoi du 1er email.

### 11.3. Préparation infrastructure

✅ **Décision n°5** : confirmation du domaine secondaire SendGrid à utiliser pour les envois (nom du domaine, statut warmup, configuration SPF/DKIM/DMARC déjà en place ?)

---

## 12. Annexes

### 12.1. Documents disponibles

| Document | Description | Statut |
|---|---|---|
| Politique de confidentialité (FR) | 13 sections RGPD-conformes | ✅ Livré |
| Politique de confidentialité (EN) | Version anglaise pour campagne USA | ✅ Livré |
| Document LIA (Legitimate Interest Assessment) | Justification documentée de l'intérêt légitime | 🔄 En cours, livraison sous 48h |
| Template du 1er email (EN) | Avec mentions CAN-SPAM + GDPR | 🔄 À produire après validation périmètre |
| Code du pipeline scraping | Python + Apify + Claude | 🔄 À produire après validation pilote |

### 12.2. Lien d'accès aux livrables

- **Google Sheet maître** : https://docs.google.com/spreadsheets/d/15Du4fIou9cOOMA5CjTz6aAtP3teTtewWd_YMU7I8Xm0
- **Site événement** : https://map.world-wellness-weekend.org/

### 12.3. Sources documentaires utilisées

Trois rapports de recherche approfondie ont nourri la stratégie présentée dans ce document. Sont référencés à titre indicatif :

- Architecture technique de prospection B2B mondiale (mai 2026)
- Analyse comparative des sources de données mondiales et stratégies d'enrichissement (mai 2026)
- Cadre juridique RGPD/CASL/CAN-SPAM et précédents jurisprudentiels 2024-2026 (mai 2026)

Ces rapports peuvent être communiqués sur demande pour étayer un point spécifique.

